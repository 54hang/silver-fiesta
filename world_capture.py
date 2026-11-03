"""World-mode integration for the original SheepSolver installation."""
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
from auto_capture import AutoCapture, write_json


class WorldCapture(AutoCapture):
    def __init__(self, output=None, auto_download=True, auto_solve=True, crypto_probe=True, publish_legacy=True):
        self._last_notice = None
        self._publish_legacy = publish_legacy
        print('\n===== SheepSolver 大世界适配版 v2 =====', flush=True)
        print('请保持本窗口打开，然后重新进入大世界关卡。', flush=True)
        super().__init__(output or ROOT / 'runtime/world', auto_download, auto_solve, crypto_probe)

    def status(self, **changes):
        super().status(**changes)
        write_json(self.out / 'service_lease.json', {'running': True, 'pid': os.getpid()})
        notice = (self.state.get('phase'), self.state.get('seed_received'),
                  self.state.get('solver'), self.state.get('seed_source'),
                  self.state.get('message'))
        if notice != self._last_notice:
            self._last_notice = notice
            message = self.state.get('message', '')
            if self.state.get('phase') == 'waiting_for_seed_decryption':
                message = ('已收到加密种子，正在验证游戏本机解密参数。'
                           '若一直停在此处，需要在保持抓包的情况下正常完成或失败一局，'
                           '让脚本取得同一加密版本的结算验证数据；之后重新进入目标关卡。')
            solver = self.state.get('solver')
            if solver == 'running':
                message = '当前关卡牌型已还原，正在限时搜索并独立验证完整路线。'
            elif solver == 'solved':
                message = '完整路线已通过回放验证。请打开本项目的“查看大世界路线.cmd”。'
            elif solver in ('no_solution_within_limit', 'timed_out'):
                message = '本轮预算内未找到完整路线；可以运行“solve-local.cmd”重新搜索。'
            print('=====> ' + message, flush=True)
            if self.state.get('seed_source'):
                print('=====> 种子验证来源: ' + self.state['seed_source'], flush=True)

    def finalize(self):
        super().finalize()
        if not self.current or not self.state.get('complete'):
            return
        current_map = Path(self.state['current_map'])
        payload = json.loads(current_map.read_text(encoding='utf-8'))
        if payload.get('_acquisition', {}).get('session') != self.current['id']:
            raise ValueError('地图与当前局不匹配')
        if self._publish_legacy:
            write_json(ROOT / 'online_data.json', payload)

    def solve_current(self, session, map_path):
        from color_rules import compatibility
        data = json.loads(map_path.read_text(encoding='utf-8'))
        if compatibility(data) not in ('standard', 'color_shuffle', 'energy_alien') or data.get('_resumed_state'):
            with self.lock:
                if self.current and self.current['id'] == session:
                    self.status(solver='unsupported_state', message='地图已还原，但当前特殊规则或已进行牌槽状态尚不支持求解。')
            return
        output = map_path.parent / 'solution'
        output.mkdir(exist_ok=True)
        command = [sys.executable, str(SUPPORT / 'solve_verified_map.py'), '--map', str(map_path),
                   '--time-limit', '60', '--mode', 'level-top', '--output', str(output)]
        with self.lock:
            if not self.current or self.current['id'] != session:
                return
            self.status(solver='running')
        env = dict(os.environ, PYTHONPATH=os.pathsep.join((str(ROOT), str(SUPPORT))), PYTHONUTF8='1')
        state = 'no_solution_within_limit'
        try:
            with (output / 'solver-process.log').open('w', encoding='utf-8') as log:
                result = subprocess.run(command, cwd=SUPPORT, env=env, stdout=log, stderr=log,
                                        creationflags=subprocess.CREATE_NO_WINDOW, timeout=80)
            answer_path = output / 'solution.json'
            if result.returncode == 0 and answer_path.exists():
                from desktop_assistant import validate_solution
                answer = json.loads(answer_path.read_text(encoding='utf-8'))
                if answer.get('validated') is not True or answer['map_sha256'] != hashlib.sha256(map_path.read_bytes()).hexdigest():
                    raise ValueError('答案未匹配当前地图')
                validate_solution(answer)
                state = 'solved'
        except subprocess.TimeoutExpired:
            state = 'timed_out'
        except (ValueError, OSError, KeyError):
            state = 'validation_failed'
        with self.lock:
            if self.current and self.current['id'] == session:
                self.status(solver=state, solution_path=str(output / 'solution.json') if state == 'solved' else None)

    def done(self):
        super().done()
        write_json(self.out / 'service_lease.json', {'running': False, 'pid': os.getpid()})


if __name__.startswith('__mitmproxy_script__.'):
    addons = [WorldCapture()]
