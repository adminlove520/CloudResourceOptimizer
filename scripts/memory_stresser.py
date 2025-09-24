#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
内存占用脚本
用于根据指定大小占用系统内存
"""

import sys
import re
import time


def print_help():
    """打印帮助信息"""
    print('Usage: ')
    print('  python memory_stresser.py 100MB')
    print('  python memory_stresser.py 1GB')


if __name__ == "__main__":
    if len(sys.argv) == 2:
        pattern = re.compile('^(\\d*)([M|G]B)$')
        match = pattern.match(sys.argv[1].upper())
        if match:
            num = int(match.group(1))
            unit = match.group(2)
            print(f"正在占用 {sys.argv[1]} 内存...")
            
            if unit == 'MB':
                s = ' ' * (num * 1024 * 1024)
            else:
                s = ' ' * (num * 1024 * 1024 * 1024)
            
            try:
                # 保持内存占用，直到被终止
                while True:
                    time.sleep(60)
                    # 访问一下变量，防止被垃圾回收
                    _ = len(s)
            except KeyboardInterrupt:
                print("已释放内存")
        else:
            print_help()
    else:
        print_help()