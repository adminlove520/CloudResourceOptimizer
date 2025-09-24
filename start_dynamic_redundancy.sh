#!/bin/bash

# CloudResourceOptimizer启动脚本(Linux版)

# 检查Python是否安装
if ! command -v python3 &> /dev/null
then
    echo "错误：未找到Python3。请先安装Python 3.6或更高版本。"
    exit 1
fi

# 检查是否以root权限运行
if [ "$(id -u)" != "0" ]
  then echo "警告：建议以root权限运行脚本，以便更好地控制系统资源"
fi

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 进入脚本目录
cd "$SCRIPT_DIR"

# 检查并安装依赖
install_deps() {
    echo "正在检查依赖包..."
    
    # 检查pip是否安装
    if ! command -v pip3 &> /dev/null
then
        echo "未找到pip3，尝试安装..."
        
        # 根据不同的Linux发行版安装pip
        if [ -f /etc/centos-release ] || [ -f /etc/redhat-release ]; then
            # CentOS/RHEL
            yum install -y python3-pip
        elif [ -f /etc/lsb-release ]; then
            # Ubuntu/Debian
            apt-get update && apt-get install -y python3-pip
        elif [ -f /etc/kylin-release ]; then
            # 麒麟系统
            apt-get update && apt-get install -y python3-pip
        elif [ -f /etc/openeuler-release ]; then
            # OpenEuler
            dnf install -y python3-pip
        else
            echo "无法识别的Linux发行版，尝试通用安装方法..."
            python3 -m ensurepip --upgrade
        fi
    fi
    
    # 安装依赖包
    echo "正在安装依赖包..."
    pip3 install -r requirements.txt
}

# 检测Linux发行版
check_linux_distro() {
    if [ -f /etc/centos-release ]; then
        echo "检测到CentOS系统"
    elif [ -f /etc/lsb-release ]; then
        echo "检测到Ubuntu/Debian系统"
    elif [ -f /etc/kylin-release ]; then
        echo "检测到麒麟系统"
    elif [ -f /etc/openeuler-release ]; then
        echo "检测到OpenEuler系统"
    else
        echo "检测到未知Linux发行版"
    fi
}

# 显示系统信息
show_system_info() {
    echo "\n=== 系统信息 ==="
    echo "操作系统: $(uname -a)"
    check_linux_distro
    echo "Python版本: $(python3 --version)"
    echo "总内存: $(free -h | awk '/Mem/ {print $2}')"
    echo "CPU核心数: $(nproc)"
    echo "磁盘挂载点: $(df -h | grep -v tmpfs | grep -v devtmpfs | awk '{print $6}' | tail -n +2 | tr '\n' ' ' | sed 's/ $//')"
    echo "================\n"
}

# 主函数
main() {
    # 显示系统信息
    show_system_info
    
    # 安装依赖
    if [ "$1" != "--no-deps" ]; then
        install_deps
    fi
    
    # 运行主脚本
    echo "正在启动CloudResourceOptimizer..."
    python3 scripts/dynamic_redundancy.py
    
    # 脚本退出后处理
    if [ $? -ne 0 ]; then
        echo "程序执行出错，请查看logs目录下的日志文件了解详情。"
    fi
}

# 运行主函数
main "$@"