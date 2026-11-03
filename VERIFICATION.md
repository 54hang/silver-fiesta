# 核查报告 / Verification audit

核查日期 / Date: 2026-11-03. Source reviewed: public `main` commit `f174be564968e2de24fb527e3e492e659de9fb04` before this documentation update.

## 可复核证据 / Reproducible evidence

| 声明 / Claim | 结果 / Finding | 证据 / Evidence |
| --- | --- | --- |
| 已上传四个 EXE / Four EXEs published | 确认 / Confirmed | Repository contains FastOriginalSolver, EnergySearch, SolverPlayback and SheepClicker.Diagnostics; v2.0.1 has a ZIP asset. |
| 源码测试 / Source tests | 40 passed, 16 skipped, 0 failed / 56 | Fresh test run against sources downloaded from public main; skipped upstream JS/live screenshot fixtures are absent. |
| 发布文件哈希 / File hashes | 107/107 matched before edits | Original SHA256SUMS.json checked against downloaded repository files. This proves consistency with the manifest, not program safety. |
| 第一关绿色背景修复 / Green-background fix | 截图回归通过 / Screenshot regression passed | test_world_green identifies only tutorial level and rejects an extra tile. It does not click a live game. |
| 合成版本 209 / Synthetic version 209 | 6-tile integration passed | test_world_integration uses synthetic encryption, materialization, native search and independent replay. Not a live protocol certification. |
| F8/F9、会话与路线检查 / Hotkeys and gates | 源码存在 / Present in source | world_solution.py and native/clicker/SolverPlayback.cs; full live effectiveness unverified. |

Reproduce from the repository root after installing Python dependencies and building native executables:

```powershell
./.venv/Scripts/python.exe -m pip install -r requirements-world-test.txt
$env:PYTHONPATH="$PWD;$PWD\world_support;$PWD\world_support\tests"
./.venv/Scripts/python.exe -m unittest discover -s world_support/tests -v
```

This review used the existing local Python 3.12 environment with Node.js on PATH. It did not establish a clean-machine installation or a full Windows compatibility matrix. Tests executed bundled native binaries; they did not send mouse input to WeChat. No binary reproducible-build claim is made.

## 历史记录与未验证部分 / Historical and unverified claims

历史本机记录曾显示一局真实版本 209 地图还原及 228 步独立回放成功。该数据含实时种子与会话信息，未公开，因此不是可由公开夹具独立重现的证明。公开测试不能扩大解释为所有版本 209 关卡兼容。

Historical local observations include one live version-209 map and a validated 228-step offline route. The private live dataset is not included; public tests do not independently prove that historical observation or universal compatibility.

**未验证 / Not verified:** full automatic live completion; server-confirmed victory; all special rules/layouts; reliable account safety; interruption recovery through the root launcher; clean-machine installation.

## 修正的误导空间 / Documentation corrections

- “支持普通、颜色、能量规则”改为“有相关实现和离线测试”，不声称每类实局均通关。 Rule implementations/offline tests are not live-win proof.
- 明确采集自动搜索、show 和 solve 默认用最后一关；play 才按屏幕选关并必要时求解。 Capture/show/solve default to the last map; play selects the visible level.
- 明确 prepare 只核对已有答案，不会自动求解。 Prepare requires an existing route.
- 明确只读进程内存扫描和本机运行数据保存；发布包不含实时数据不代表运行时不落盘。 Explain memory probing and local persistence.
- 英文文档不意味着界面已英文化。 English docs do not translate runtime UI.
- 不承诺“无幻觉”或“保证通关”；只列证据及验证边界。 No blanket hallucination-free or guaranteed-win claim.

## 许可证和运行信息 / License and runtime data

AGPL-3.0 license files and upstream revision records exist. This is a file-level provenance check, not a comprehensive legal opinion. The reviewed public tree has no runtime directory, virtualenv, certificate private keys or live acquisition sessions. Synthetic test keys are intentional fixtures, not production credentials.

`world-verification.json` is a summary, not an independent certificate. Historical checks are distinguished from this review's fresh test run. Existing v2.0.1 binaries are unchanged by this documentation update; updated documentation packages must carry newly generated hashes.
