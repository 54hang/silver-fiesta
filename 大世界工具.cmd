@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
title 羊了个羊大世界工具
:menu
cls
echo 羊了个羊大世界工具
echo.
echo 1. 启动抓包（保留窗口，再进入游戏）
echo 2. 查看已求解路线
echo 3. 核对当前棋盘
echo 4. 自动执行当前关路线（F8 暂停，F9 停止）
echo 0. 退出
echo.
choice /c 12340 /n /m "请选择："
if errorlevel 5 exit /b
if errorlevel 4 goto play
if errorlevel 3 goto prepare
if errorlevel 2 goto show
start "" "%~dp0capture-world.cmd"
goto menu
:show
start "" "%~dp0查看大世界路线.cmd"
goto menu
:prepare
start "" "%~dp0核对大世界棋盘.cmd"
goto menu
:play
start "" "%~dp0自动执行大世界路线.cmd"
goto menu
