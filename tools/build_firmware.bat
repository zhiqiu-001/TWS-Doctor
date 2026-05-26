@echo off
echo ========================================
echo ESP32 TWS Doctor - 固件编译工具
echo ========================================
echo.

cd /d "%~dp0..\firmware_esp32s3"

if not exist "CMakeLists.txt" (
    echo 错误: 找不到 CMakeLists.txt，确保在正确的目录下
    pause
    exit /b 1
)

echo 正在编译固件...
call idf.py build

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo 编译成功！
    echo ========================================
) else (
    echo.
    echo ========================================
    echo 编译失败！
    echo ========================================
)

pause
