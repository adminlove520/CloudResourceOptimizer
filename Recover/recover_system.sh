#!/bin/bash

# CloudResourceOptimizer - 系统资源恢复Shell脚本
# 用于在Linux系统上方便地运行Python恢复脚本

# 设置目录变量
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$ROOT_DIR/logs"
PYTHON_SCRIPT="$SCRIPT_DIR/recover_system.py"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3安装。请先安装Python3。"
    exit 1
fi

# 打印脚本信息
cat << "EOF"
=======================================================
             系统资源恢复工具
=======================================================
此工具将：
1. 停止所有资源占用进程（CPU、内存、磁盘占用脚本）
2. 清理临时文件
3. 优化系统资源
4. 显示系统状态变化
=======================================================
日志文件将保存在：$LOG_DIR
=======================================================
EOF

# 运行Python恢复脚本
sudo python3 "$PYTHON_SCRIPT"

# 检查Python脚本执行结果
if [ $? -ne 0 ]; then
    echo "恢复过程中发生错误"
    exit 1
fi