# SheepSolver World — Windows 大世界适配版 v2.0.1

为微信《羊了个羊》羊羊大世界提供当前局地图采集、限时路线搜索、独立回放验证和棋盘核对后的逐步点击。

**第三方工具可能违反游戏规则并导致封号。并非官方项目，不保证通关或账号安全。**

## 安装

需要 Windows 10/11、Python 3.12（含 `py` 启动器）、Node.js，以及系统自带 .NET Framework 4 编译器。
解压到普通可写文件夹，在 PowerShell 中运行 `./setup-world.ps1`。脚本安装依赖并从随附源码重新编译四个程序。
如果本机 PowerShell 策略限制脚本，可对当前这次调用使用 `powershell -ExecutionPolicy Bypass -File .\setup-world.ps1`。

首次使用需要自行配置手动代理 `127.0.0.1:6666`，并信任本机生成的 mitmproxy 证书；证书位于 `runtime/mitmproxy`。本项目不会自动修改代理或安装证书。
不要分享该目录的私钥，也不要将他人的证书私钥装入自己的系统。使用完成后关闭系统手动代理。

## 使用

1. 启动 `capture-world.cmd`，保持窗口打开，再重新进入大世界关卡，先不要点牌。
2. 等待完整地图与“完整路线已通过回放验证”提示。加密种子验证可能需要在采集持续开启时正常完成或失败一局，再重新进入下一局。
3. 保持棋盘完整可见、牌槽为空，收起微信侧栏。执行 `自动执行大世界路线.cmd`，程序识别屏幕关次，必要时求解，再核对棋盘后点击。
4. F8 暂停/继续，F9 停止。一次执行一关，下一关稳定后再运行一次。以游戏成功画面为准。

`大世界工具.cmd` 提供菜单；`查看大世界路线.cmd` 查看路线；`核对大世界棋盘.cmd` 只核对棋盘。详见 [大世界使用说明](大世界使用说明.md)。

本包不含虚拟环境、认证令牌、抓包记录、实时种子、用户证书、缓存会话和个人快捷方式。运行时在本机生成所需目录。

## 修复与限制

- `.map` 二进制地图及独立加密种子响应适配；当前请求前缀验证通过后才接受解密结果。
- 支持普通、颜色和能量规则；当前局身份、地图哈希、独立路线回放和采集进程状态均需校验。
- 按屏幕选择第一关或后续关，修复浅绿色背景被误识别为牌面导致第一关被拒绝的问题。
- 不支持自动使用移出等道具、手动点牌后的恢复、所有特殊规则或所有布局；未通过核对时停止。
- 当前窗口标题适配“羊了个羊：星球”；客户端变化可能需要再适配。

已验证真实版本 209 的一局地图还原和 228 步路线回放，但**尚未验证自动点击完成实局、服务器判定通关**。搜索成功不代表实局通关。

## 验证

安装测试依赖后，在项目根目录的 PowerShell 中运行：

```powershell
./.venv/Scripts/python.exe -m pip install -r requirements-world-test.txt
$env:PYTHONPATH="$PWD;$PWD\world_support;$PWD\world_support\tests"
./.venv/Scripts/python.exe -m unittest discover -s world_support/tests -v
```

部分维护分支客户端/截图夹具未随项目发布，对应测试跳过。绿色背景回归夹具仅含游戏画面和匿名地图结构；地图来源时间、会话标识及种子已剔除。

## 来源与许可证

基于 [NB-Dragon/SheepSolver](https://github.com/NB-Dragon/SheepSolver)，并集成 [Lda2138/SheepSolver](https://github.com/Lda2138/SheepSolver) 的协议、规则、搜索及点击实现；版本分别见 `source-version.json` 和 `world_support/SOURCE.json`。

按 **GNU AGPL-3.0** 发布。原许可证和来源随附；本仓库包含本地修改和全部随附二进制对应的 C# 源码、编译脚本。原项目说明见 `README.upstream.md`。游戏名称和游戏画面属于其各自权利人。
