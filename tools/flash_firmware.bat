@echo off
echo ========================================
echo ESP32 TWS Doctor - 固件烧录工具
echo ========================================
echo.

cd /d "%~dp0..\firmware_esp32s3"

if not exist "CMakeLists.txt" (
    echo 错误: 找不到 CMakeLists.txt，确保在正确的目录下
    pause
    exit /b 1
)

echo 正在烧录固件...
call idf.py flash

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo 烧录成功！
    echo ========================================
) else (
    echo.
    echo ========================================
    echo 烧录失败！
    echo ========================================
)

pause
