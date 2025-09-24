@echo off

REM CloudResourceOptimizer启动批处理文件

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到Python。请先安装Python 3.6或更高版本。
    pause
    exit /b 1
)

REM 进入脚本目录
cd /d "%~dp0"

REM 运行主脚本
python scripts\dynamic_redundancy.py

REM 脚本退出后暂停
if %errorlevel% neq 0 (
    echo 程序执行出错，请查看日志了解详情。
)

pause