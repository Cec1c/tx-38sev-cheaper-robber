@echo off
chcp 65001 >nul
cd /d %~dp0
echo ================ 早上抢购自检 ================
python morning_check.py
echo.
echo ================ 启动两场监听 ================
python launch_today.py
echo.
pause
