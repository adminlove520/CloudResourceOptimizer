@echo off

REM CloudResourceOptimizer - 系统资源恢复批处理脚本
REM 用于在Windows系统上方便地运行Python恢复脚本

SET "SCRIPT_DIR=%~dp0"
SET "ROOT_DIR=%SCRIPT_DIR%.."
SET "LOG_DIR=%ROOT_DIR%\logs"
SET "PYTHON_SCRIPT=%SCRIPT_DIR%recover_system.py"

REM 创建日志目录
IF NOT EXIST "%LOG_DIR%" MKDIR "%LOG_DIR%"

REM 检查Python是否安装
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO 错误: 未找到Python安装。请先安装Python并确保已添加到系统PATH。
    PAUSE
    EXIT /B 1
)

REM 打印脚本信息
ECHO ======================================================
ECHO             系统资源恢复工具
ECHO ======================================================
ECHO 此工具将：
ECHO 1. 停止所有资源占用进程（CPU、内存、磁盘占用脚本）
ECHO 2. 清理临时文件
ECHO 3. 优化系统资源
ECHO 4. 显示系统状态变化
ECHO ======================================================
ECHO 日志文件将保存在：%LOG_DIR%
ECHO ======================================================

REM 运行Python恢复脚本
python "%PYTHON_SCRIPT%"

REM 检查Python脚本执行结果
IF %ERRORLEVEL% NEQ 0 (
    ECHO 恢复过程中发生错误
    PAUSE
    EXIT /B 1
)

PAUSE