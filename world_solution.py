"""Read, solve or display only the currently captured world-session route."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
SUPPORT = ROOT / 'world_support'
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SUPPORT))


def current():
    status_path = ROOT / 'runtime/world/status.json'
    if not status_path.exists():
        raise ValueError('尚未运行大世界适配版抓包脚本。')
    status = json.loads(status_path.read_text(encoding='utf-8'))
    if status.get('complete') is not True or not status.get('current_map'):
        raise ValueError('当前局牌型尚未完整还原。' + status.get('message', ''))
    path = Path(status['current_map']).resolve()
    if not path.is_relative_to((ROOT / 'runtime/world/sessions').resolve()):
        raise ValueError('地图不属于本项目的采集目录。')
    data = json.loads(path.read_text(encoding='utf-8'))
    if data.get('_acquisition', {}).get('session') != status.get('session'):
        raise ValueError('地图与当前局号不一致。')
    return status, path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['status', 'solve', 'show', 'prepare', 'play'])
    parser.add_argument('--seconds', type=int, default=60)
    args = parser.parse_args()
    if not 1 <= args.seconds <= 300:
        parser.error('--seconds must be between 1 and 300')
    status, path = current()
    if args.action == 'status':
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return
    raw = None
    if args.action in ('prepare', 'play'):
        import app_bridge
        app_bridge.OUT = ROOT / 'runtime/world'
        raw = app_bridge.capture_snapshot(ROOT / 'runtime/world/board-now.png')
        selection = app_bridge.inspect_board(path.parent, raw, len(status['map_ids']))
        if selection.get('resume'):
            raise ValueError('当前关已有点击记录。自动从头执行已停用，需要核对断点后才能继续。')
        path = path.parent / ('map_{}.json'.format(selection['level']))
        print('已识别屏幕上是本局第 {} 关。'.format(selection['level'] + 1), flush=True)
    data = json.loads(path.read_text(encoding='utf-8'))
    identity = data.get('_acquisition', {})
    index = identity.get('level_index')
    if (identity.get('session') != status.get('session') or not isinstance(index, int)
            or not 0 <= index < len(status['map_ids']) or identity.get('map_md5') != status['map_ids'][index]):
        raise ValueError('地图与当前关次身份不一致。')
    output = path.parent / ('solution' if index == len(status['map_ids']) - 1 else 'level_{}_solution'.format(index))
    if args.action == 'solve' or (args.action == 'play' and not (output / 'solution.json').exists()):
        env = dict(os.environ, PYTHONPATH=os.pathsep.join((str(ROOT), str(SUPPORT))), PYTHONUTF8='1')
        result = subprocess.run([sys.executable, str(SUPPORT / 'solve_verified_map.py'), '--map', str(path),
                                 '--time-limit', str(args.seconds), '--mode', 'level-top', '--output', str(output)],
                                cwd=SUPPORT, env=env)
        if result.returncode:
            raise ValueError('本次搜索未得到完整且通过验证的路线。')
    answer_path = output / 'solution.json'
    if not answer_path.exists():
        raise ValueError('当前关卡尚无完整路线；可运行 solve-local.cmd 搜索。')
    answer = json.loads(answer_path.read_text(encoding='utf-8'))
    from desktop_assistant import validate_solution
    if answer.get('validated') is not True or answer.get('map_sha256') != hashlib.sha256(path.read_bytes()).hexdigest():
        raise ValueError('答案与当前地图不符。')
    validate_solution(answer)
    # Recheck the active capture after a potentially long search.
    newest, newest_path = current()
    if newest.get('session') != status.get('session') or newest_path.parent != path.parent:
        raise ValueError('搜索期间已换局，请使用新局路线。')
    print('路线回放验证通过，共 {} 步。'.format(len(answer['sequence'])))
    if args.action == 'show':
        os.startfile(str(output / '点击预演.html'))
    if args.action in ('prepare', 'play'):
        import app_bridge
        app_bridge.OUT = ROOT / 'runtime/world'
        data = json.loads(path.read_text(encoding='utf-8'))
        mode = 'world' if '/world/' in status.get('source_path', '') else 'daily'
        level = data['_acquisition']['level_index']
        lease = json.loads((ROOT / 'runtime/world/service_lease.json').read_text(encoding='utf-8'))
        if not lease.get('running'):
            raise ValueError('请保持大世界抓包窗口打开。')
        # Search may take a minute; capture and recheck the board again.
        raw = app_bridge.capture_snapshot(output / 'current-board.png')
        prepared = app_bridge.prepare(path.parent, path, data, level, mode,
                                      image_path=raw, solution_path=answer_path, refit=True)
        newest, _ = current()
        if newest.get('session') != status.get('session'):
            raise ValueError('棋盘核对期间已经换局，停止执行。')
        if args.action == 'prepare':
            print(prepared['message'])
            os.startfile(prepared['preview_path'])
        else:
            print('棋盘已核对，开始自动执行。F8 暂停/继续，F9 停止。请保持游戏窗口可见且不移动。', flush=True)
            result = subprocess.run([str(SUPPORT / 'SolverPlayback.exe'), prepared['plan_path']], cwd=SUPPORT)
            if result.returncode:
                raise ValueError('执行已停止，请查看上方的牌面核对提示；不要从头重复点击。')
            print('本关计划已执行；是否通关请以游戏成功画面为准。')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError) as error:
        print('=====> ' + str(error))
        raise SystemExit(1)
