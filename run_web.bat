@echo off
chcp 65001 > nul
echo ============================================
echo   规则解剖引擎 — Web 服务
echo ============================================
echo.
echo 本机访问: http://localhost:8000
echo.
REM 自动获取本机局域网 IP
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /i "IPv4" ^| findstr /v "127.0.0.1"') do set ip=%%i
set ip=%ip: =%
if not "%ip%"=="" (
    echo 手机访问（同一 WiFi）: http://%ip%:8000
    echo.
    start http://%ip%:8000
) else (
    echo 手机访问: 先查电脑 IP（ipconfig），然后浏览器输入 http://IP:8000
    echo.
    start http://localhost:8000
)
echo 按 Ctrl+C 停止服务器
echo ============================================
echo.
python "%~dp0run.py" --serve %*
pause
