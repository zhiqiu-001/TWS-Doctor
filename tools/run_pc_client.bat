@echo off
echo ========================================
echo ESP32 TWS Doctor - 启动上位机
echo ========================================
echo.

cd /d "%~dp0..\pc_client_pyqt"

if not exist "main.py" (
    echo 错误: 找不到 main.py
    pause
    exit /b 1
)

echo 正在检查依赖...
python -c "import PyQt6" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 未找到依赖，正在安装...
    pip install -r requirements.txt
)

echo.
echo 启动上位机...
python main.py

pause
