@echo off
chcp 65001 >nul
title 思维解剖模型 V1.0 — 多模型智囊团深度辩论

cd /d C:\Users\雷万煜\LogicJudgeModel

echo ╔══════════════════════════════════════════════════════════╗
echo ║          思维解剖模型 V1.0                              ║
echo ║  基于 40+ 本书籍的多模型智囊团深度辩论系统              ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 可用命令：
echo   dissect ^<问题^>  解剖分析（自动检测模式）
echo   game   ^<问题^>  博弈分析（模式A）
echo   nav    ^<问题^>  方向导航（模式B）
echo   debate ^<问题^>  多模型智囊团深度辩论
echo   deep   ^<问题^>  解剖分析 + 深度辩论全流程
echo   help            帮助
echo   exit            退出
echo.

:loop
set /p cmd="❯ "

if /i "%cmd%" == "exit" exit /b
if /i "%cmd%" == "quit" exit /b
if /i "%cmd%" == "help" (
    echo 命令同上。直接输入问题默认进入解剖分析。
    goto loop
)

if /i "%cmd:~0,7%" == "dissect" (
    python 思维解剖.py --mode auto "%cmd:~8%"
    echo.
    goto loop
)
if /i "%cmd:~0,5%" == "game " (
    python 思维解剖.py --mode a "%cmd:~5%"
    echo.
    goto loop
)
if /i "%cmd:~0,4%" == "nav " (
    python 思维解剖.py --mode b "%cmd:~4%"
    echo.
    goto loop
)
if /i "%cmd:~0,7%" == "debate " (
    python 思维解剖.py --debate "%cmd:~7%"
    echo.
    goto loop
)
if /i "%cmd:~0,5%" == "deep " (
    python 思维解剖.py --deep "%cmd:~5%"
    echo.
    goto loop
)

:: 默认
if defined cmd (
    python 思维解剖.py --mode auto "%cmd%"
    echo.
)
goto loop
