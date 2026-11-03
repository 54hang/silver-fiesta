# SheepSolver World — 中文说明

[中文说明](README.zh-CN.md) | [English documentation](README.en.md)


本项目采集微信《羊了个羊》大世界的关卡数据，限时搜索路线，独立回放验证后，尝试在棋盘核对通过时自动点击。**不是官方项目，不保证通关或账号安全，使用第三方工具可能导致账号处罚。**

### 安装

准备 Windows、Python 3.12（含 `py` 启动器）、Node.js，以及 .NET Framework 4 的 C# 编译器。Windows 10/11 是预期运行环境，未做完整系统版本兼容矩阵测试。

下载仓库源码或 Release ZIP，解压到可写文件夹，在 PowerShell 运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup-world.ps1
```

安装脚本会联网安装依赖，并从随附 C# 源码重新编译四个 EXE。EXE 不是一键独立安装包，仍需要 Python 环境和配置。

### 使用

1. 启动 `capture-world.cmd`，保持窗口打开；配置手动代理 `127.0.0.1:6666` 和本机 mitmproxy 证书，再重新进入目标关卡，先不要点牌。
2. 等待种子校验、地图还原和搜索。默认自动搜索捕获会话的最后一关；“完整路线已通过回放验证”不一定表示屏幕当前第一关已有答案。
3. 让游戏窗口完整显示、收起微信侧栏、牌槽为空；运行 `自动执行大世界路线.cmd`。它会识别屏幕显示的关次，必要时为该关搜索，核对后才尝试点击。
4. F8 暂停/继续，F9 停止。一次调用执行一关；进入下一关后再次运行。以游戏成功画面为准。

`查看大世界路线.cmd`、`solve-local.cmd` 默认针对会话的最后一关；`核对大世界棋盘.cmd` 不会点击，也不会自动求解，需对应关卡已有答案。

### 已知限制与数据

- 源码实现普通、颜色和能量规则，但没有逐类微信实局通关证明；不支持所有特殊牌、道具和屏幕布局。
- 当前入口拒绝手动点牌后的未知状态及断点续接；不要中断后从头重放。
- 当前窗口标题要求“羊了个羊：星球”。首次证书配置需用户完成，程序不会自动安装证书或更改系统代理。
- 采集器会尝试只读扫描游戏宿主进程内存，寻找游戏解密参数；参数仅留在内存。失败时可能需要同一采集进程内的正常结算数据，不能保证成功。
- 运行时会在本机保存地图、种子、棋盘截图、计划和诊断。发布包排除这些实时数据和证书私钥，不代表工具运行时不存储数据。退出后关闭手动代理。

### 验证边界

2026-11-03 从公开仓库下载的源码复测：**56 项中 40 通过、16 跳过、0 失败**；107 项文件哈希全部匹配。测试没有向微信发送鼠标输入。

本机历史记录显示一次真实版本 209 地图还原、228 步离线回放通过；这份实时数据没有公开，外部读者无法仅靠仓库复现这一历史实局记录。公开的合成版本 209 测试只有 6 张牌。绿色背景修复已通过公开第一关截图测试。

**尚未验证真实自动点击完整通关、服务器判定成功或账号安全。** 测试通过不等于能稳定通关。详见 [核查报告](VERIFICATION.md)。

## 来源与许可证


Based on [NB-Dragon/SheepSolver](https://github.com/NB-Dragon/SheepSolver), with protocol, rules, search and playback code from [Lda2138/SheepSolver](https://github.com/Lda2138/SheepSolver). Revisions: `source-version.json` and `world_support/SOURCE.json`.

GNU **AGPL-3.0**; licenses, C# sources and build scripts are included. `README.upstream.md` is historical upstream documentation, not the current support contract. Game names and images belong to their respective owners. English documentation does not imply an English application UI; runtime messages and menu filenames remain mostly Chinese.
