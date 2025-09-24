#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CPU占用脚本
用于占用系统CPU资源
"""

import sys
import time
import threading
import multiprocessing


def cpu_intensive_task():
    """CPU密集型任务"""
    while True:
        # 执行一个CPU密集型计算
        _ = [i * i for i in range(10000)]


def print_help():
    """打印帮助信息"""
    print('Usage: ')
    print('  python cpu_stresser.py')
    print('  python cpu_stresser.py --threads 2')


if __name__ == "__main__":
    # 默认使用所有CPU核心
    num_threads = multiprocessing.cpu_count()
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == '--help' or sys.argv[1] == '-h':
            print_help()
            sys.exit(0)
        elif sys.argv[1] == '--threads' and len(sys.argv) > 2:
            try:
                num_threads = int(sys.argv[2])
                num_threads = max(1, min(num_threads, multiprocessing.cpu_count()))
            except ValueError:
                print("无效的线程数，使用默认值")
    
    print(f"正在使用 {num_threads} 个线程占用CPU...")
    
    # 创建线程
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=cpu_intensive_task, daemon=True)
        threads.append(thread)
        thread.start()
    
    try:
        # 主线程保持运行
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("已停止CPU占用")