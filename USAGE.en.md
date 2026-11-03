# English usage guide

[中文说明](README.zh-CN.md) | [English documentation](README.en.md)

Read [README.md](README.md) for installation, account risks and verification limits. The user interface and launch filenames remain mostly Chinese.

## First setup

Install Python 3.12 with the Windows `py` launcher, Node.js on PATH, and .NET Framework 4 with its C# compiler. Run `setup-world.ps1` from PowerShell; it creates `.venv`, installs dependencies and rebuilds four executables. A clean-machine installation has not been tested end to end.

Start `capture-world.cmd` before configuring the manual proxy at `127.0.0.1:6666`. For HTTPS interception, trust the certificate generated on this computer in `runtime/mitmproxy`, following mitmproxy's Windows certificate instructions. The tool does not install it automatically. Never share the private key or trust somebody else's private-key bundle.

## Each session

1. Open `capture-world.cmd` once. Keep that window open; a second process may conflict on port 6666.
2. Re-enter world mode in WeChat. Do not click tiles, shuffle or use props.
3. Wait for seed validation. If it needs settlement evidence, keep capture running, finish or lose a game normally, then enter a new game. Restarting capture loses in-memory crypto evidence. This method may still fail.
4. Capture searches the last map in the session, usually the main level. Its success message does not mean the visible tutorial already has a route.
5. Collapse the WeChat sidebar and keep the entire board visible with an empty tray. Run `自动执行大世界路线.cmd` (play). It selects the visible level, searches if needed, verifies the route and geometry, and attempts guarded clicks. Keep the window stationary and do not operate the game concurrently.
6. Use F8 to pause/resume or F9 to stop. Only one level is executed per invocation; wait for the next board to stabilize and invoke play again. Do not replay from the beginning after partial execution.
7. Check the game's own success screen. Close capture and disable the system manual proxy after use.

## Other launchers

| File | Behavior |
| --- | --- |
| `大世界工具.cmd` | Chinese menu for capture, route preview, board check and play |
| `查看大世界路线.cmd` | Preview the last captured level's validated route |
| `solve-local.cmd` | Search the last captured level, default budget 60 seconds |
| `核对大世界棋盘.cmd` | Select and check the visible level; requires its route already exists; does not click or search |
| `自动执行大世界路线.cmd` | Select, search if necessary, check and attempt one level |

The 60-second search budget excludes some validation and process overhead, so total elapsed time can exceed 60 seconds.

## Troubleshooting

- **Waiting for seed/decryption:** follow the capture prompt; do not treat encrypted bytes as a usable seed.
- **Waiting for board alignment:** collapse the sidebar and show the full board. The current code expects the exact window title `羊了个羊：星球` and screenshots normalized to 336×622.
- **Map mismatch:** stop. A changed level, stale session, partial board or layout mismatch must be investigated; never bypass the gate.
- **No route:** bounded search can fail. `solve-local.cmd` retries the last map, not necessarily the visible tutorial; play can search the visible level.
- **Network disconnect messages:** they indicate connection failures, not proof of an account ban or successful capture. Check `runtime/world/status.json` for map/solver state.
- **After manual moves or interruption:** the root launcher does not support resuming unknown or partially played boards. Start a new session rather than replaying clicks.

Local diagnostics are under `runtime/world/`. They can include real seeds, map state and screenshots; do not publish that directory or certificate private keys.
