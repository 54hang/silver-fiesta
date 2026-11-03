# SheepSolver World — English documentation

[中文说明](README.zh-CN.md) | [English documentation](README.en.md)


This Windows adaptation captures world-mode maps from the WeChat game, searches for routes within a time budget, independently replays them, and attempts guarded clicks after board alignment. **Unofficial; no guarantee of completion or account safety. Third-party tooling may result in account penalties.**

### Install and run

Install Python 3.12 with the `py` launcher, Node.js, and the .NET Framework 4 C# compiler. Windows 10/11 are intended targets, not a fully tested compatibility matrix. Extract the source or Release ZIP into a writable directory and run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup-world.ps1
```

Setup downloads Python dependencies and rebuilds four bundled executables from the included C# sources. The EXEs are components, not a standalone one-click installer.

1. Run `capture-world.cmd`; keep it open. Configure proxy `127.0.0.1:6666` and trust your locally generated mitmproxy certificate, then re-enter the target level without clicking tiles.
2. Wait for seed validation, map reconstruction and search. Automatic capture search targets the session's last level, which may differ from the level currently on screen.
3. Show the entire board, collapse the WeChat sidebar, and keep the tray empty. Run `自动执行大世界路线.cmd`. It selects the visible level, searches if needed, checks the board, and then attempts playback.
4. F8 pauses/resumes; F9 stops. One level per invocation. A finished route is not proof of server-confirmed victory.

`查看大世界路线.cmd` and `solve-local.cmd` default to the last captured level. `核对大世界棋盘.cmd` only checks an existing route; it neither searches nor clicks.

### Limits and evidence

Standard, color and energy rules have implementations; complete live wins for each rule are unverified. Unsupported props, partial-board recovery and client layouts may fail. The window title must currently be `羊了个羊：星球`.

Capture may read game-host process memory for crypto parameters, kept in memory, or require a normal settlement while the same capture process remains running. Runtime maps, seeds, screenshots and diagnostics are saved locally. Live data and certificate private keys are excluded from the published package. Disable the system proxy when finished.

Fresh tests of downloaded repository sources on 2026-11-03: **40 passed, 16 skipped, 0 failed out of 56**; all 107 manifest entries matched. Tests sent no mouse input. Historical local evidence includes one version-209 map and a 228-step offline replay; that live dataset is not published. The public synthetic version-209 test uses only six tiles. **Full live playback, server-confirmed victory and account safety remain unverified.** See [verification audit](VERIFICATION.md) and [English usage guide](USAGE.en.md).

## Attribution and license


Based on [NB-Dragon/SheepSolver](https://github.com/NB-Dragon/SheepSolver), with protocol, rules, search and playback code from [Lda2138/SheepSolver](https://github.com/Lda2138/SheepSolver). Revisions: `source-version.json` and `world_support/SOURCE.json`.

GNU **AGPL-3.0**; licenses, C# sources and build scripts are included. `README.upstream.md` is historical upstream documentation, not the current support contract. Game names and images belong to their respective owners. English documentation does not imply an English application UI; runtime messages and menu filenames remain mostly Chinese.
