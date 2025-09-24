#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
磁盘占用脚本
用于在指定磁盘创建临时大文件以增加磁盘利用率
"""

import sys
import os
import time
import random
import argparse


def print_help():
    """打印帮助信息"""
    print('Usage: ')
    print('  python disk_stresser.py --path /data --size 100MB')
    print('  python disk_stresser.py --path D:\\data --size 1GB --duration 3600')


def parse_size(size_str):
    """解析大小字符串为字节数"""
    try:
        # 匹配数字和单位
        pattern = '^(\\d+)([M|G]B)$'
        import re
        match = re.match(pattern, size_str.upper())
        if match:
            num = int(match.group(1))
            unit = match.group(2)
            if unit == 'MB':
                return num * 1024 * 1024  # MB转字节
            elif unit == 'GB':
                return num * 1024 * 1024 * 1024  # GB转字节
        # 如果格式不正确，抛出异常
        raise ValueError(f"无效的大小格式: {size_str}")
    except Exception as e:
        print(f"解析大小失败: {e}")
        sys.exit(1)


def create_temp_file(file_path, file_size_bytes, duration_seconds):
    """创建临时大文件"""
    try:
        # 确保目录存在
        dir_path = os.path.dirname(file_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        
        print(f"正在 {file_path} 创建 {file_size_bytes/1024/1024:.2f}MB 的临时文件...")
        
        # 分块写入文件
        block_size = 1024 * 1024  # 1MB块
        blocks = file_size_bytes // block_size
        remainder = file_size_bytes % block_size
        
        with open(file_path, 'wb') as f:
            for i in range(blocks):
                # 显示进度
                if i % 10 == 0:
                    progress = (i / blocks) * 100
                    print(f"进度: {progress:.1f}%")
                # 写入随机数据
                f.write(os.urandom(block_size))
            
            # 写入剩余部分
            if remainder > 0:
                f.write(os.urandom(remainder))
        
        print(f"文件创建完成，大小: {os.path.getsize(file_path)/1024/1024:.2f}MB")
        print(f"将在 {duration_seconds} 秒后删除文件")
        
        # 等待指定时间后删除文件
        try:
            time.sleep(duration_seconds)
        except KeyboardInterrupt:
            print("\n接收到中断信号，立即删除文件")
        
        # 删除临时文件
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"已删除临时文件: {file_path}")
        
    except Exception as e:
        print(f"创建临时文件失败: {e}")
        # 清理已创建的文件
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"已清理临时文件: {file_path}")
            except:
                pass
        sys.exit(1)


if __name__ == "__main__":
    # 使用argparse解析命令行参数
    parser = argparse.ArgumentParser(description='磁盘占用工具')
    parser.add_argument('--path', required=True, help='临时文件路径')
    parser.add_argument('--size', required=True, help='文件大小，格式如100MB或1GB')
    parser.add_argument('--duration', type=int, default=3600, help='文件保留时间(秒)，默认3600秒(1小时)')
    
    args = parser.parse_args()
    
    # 解析文件大小
    file_size_bytes = parse_size(args.size)
    
    # 生成随机文件名（如果路径是目录）
    if os.path.isdir(args.path):
        file_name = f"temp_{int(time.time())}_{random.randint(1000, 9999)}.dat"
        file_path = os.path.join(args.path, file_name)
    else:
        file_path = args.path
    
    # 创建临时文件
    create_temp_file(file_path, file_size_bytes, args.duration)