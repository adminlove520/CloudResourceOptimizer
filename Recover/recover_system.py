#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CloudResourceOptimizer - 系统资源恢复脚本
用于停止所有资源占用脚本并清理临时文件，将系统恢复到正常状态
支持Windows和Linux平台
"""

import os
import sys
import psutil
import platform
import subprocess
import time
from datetime import datetime

class SystemRecover:
    """系统恢复类，用于清理资源占用"""
    def __init__(self):
        self.system = platform.system().lower()
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """设置日志记录器"""
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"recover_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        # 简单的日志函数
        def log(message, level='INFO'):
            log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{level}] {message}\n"
            print(log_entry)
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        
        return log
    
    def stop_stresser_processes(self):
        """停止所有资源占用进程"""
        self.logger("开始停止资源占用进程...")
        
        # 定义要停止的进程名称
        stresser_scripts = [
            'cpu_stresser.py', 
            'memory_stresser.py', 
            'disk_stresser.py',
            'dynamic_redundancy.py'
        ]
        
        processes_stopped = 0
        
        try:
            # 遍历所有进程
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_info = proc.info
                    # 检查进程命令行中是否包含资源占用脚本
                    if proc_info['cmdline']:
                        cmdline_str = ' '.join(proc_info['cmdline'])
                        for script in stresser_scripts:
                            if script in cmdline_str and sys.executable in cmdline_str:
                                # 确保不是当前脚本本身
                                if os.path.basename(__file__) not in cmdline_str:
                                    self.logger(f"发现资源占用进程: PID={proc_info['pid']}, 命令: {cmdline_str}")
                                    
                                    # 优雅地终止进程
                                    proc.terminate()
                                    
                                    # 等待进程终止，最多等待5秒
                                    try:
                                        proc.wait(timeout=5)
                                        self.logger(f"成功终止进程: PID={proc_info['pid']}")
                                        processes_stopped += 1
                                    except psutil.TimeoutExpired:
                                        # 如果超时，强制终止
                                        proc.kill()
                                        self.logger(f"强制终止进程: PID={proc_info['pid']}")
                                        processes_stopped += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            self.logger(f"停止进程时发生错误: {e}", 'ERROR')
        
        self.logger(f"共停止 {processes_stopped} 个资源占用进程")
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        self.logger("开始清理临时文件...")
        
        # 定义要搜索的临时文件模式
        temp_file_patterns = [
            'temp_*.dat',  # disk_stresser创建的临时文件
        ]
        
        files_cleaned = 0
        
        try:
            # 根据平台选择要搜索的目录
            if self.system == 'windows':
                # Windows系统搜索所有数据盘
                drives = [f"{d}:\\" for d in 'DEFGHIJKLMNOPQRSTUVWXYZ' if os.path.exists(f"{d}:\\")]
                # 排除系统盘
                if 'C:\\' in drives:
                    drives.remove('C:\\')
                search_dirs = drives
            else:
                # Linux系统搜索常见数据目录
                search_dirs = ['/data', '/var/data', '/home', '/opt']
                # 添加配置目录
                config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config')
                search_dirs.append(config_dir)
            
            # 搜索并删除临时文件
            for search_dir in search_dirs:
                if os.path.exists(search_dir):
                    for root, dirs, files in os.walk(search_dir):
                        for file in files:
                            for pattern in temp_file_patterns:
                                import fnmatch
                                if fnmatch.fnmatch(file, pattern):
                                    file_path = os.path.join(root, file)
                                    try:
                                        os.remove(file_path)
                                        self.logger(f"删除临时文件: {file_path}")
                                        files_cleaned += 1
                                    except Exception as e:
                                        self.logger(f"删除文件 {file_path} 失败: {e}", 'ERROR')
        except Exception as e:
            self.logger(f"清理临时文件时发生错误: {e}", 'ERROR')
        
        self.logger(f"共清理 {files_cleaned} 个临时文件")
    
    def optimize_system(self):
        """优化系统资源"""
        self.logger("开始优化系统资源...")
        
        try:
            if self.system == 'windows':
                # Windows系统优化
                # 清理内存
                self.logger("执行Windows内存清理...")
                # 使用Windows内置工具清理内存
                subprocess.run(['powershell.exe', 'Clear-SystemMemoryCache -Immediately'], 
                              capture_output=True, text=True)
            else:
                # Linux系统优化
                # 清理页面缓存
                self.logger("清理Linux页面缓存...")
                try:
                    with open('/proc/sys/vm/drop_caches', 'w') as f:
                        f.write('3')
                    self.logger("Linux页面缓存清理成功")
                except PermissionError:
                    self.logger("需要root权限清理Linux页面缓存", 'WARNING')
        except Exception as e:
            self.logger(f"优化系统资源时发生错误: {e}", 'ERROR')
    
    def show_system_status(self):
        """显示当前系统状态"""
        self.logger("\n==== 当前系统状态 ====")
        
        # 显示CPU使用率
        cpu_usage = psutil.cpu_percent(interval=1)
        self.logger(f"CPU使用率: {cpu_usage}%")
        
        # 显示内存使用情况
        memory = psutil.virtual_memory()
        memory_used_percent = memory.percent
        memory_used_gb = memory.used / (1024 * 1024 * 1024)
        memory_total_gb = memory.total / (1024 * 1024 * 1024)
        self.logger(f"内存使用: {memory_used_percent}% ({memory_used_gb:.2f}GB/{memory_total_gb:.2f}GB)")
        
        # 显示磁盘使用情况
        self.logger("磁盘使用情况:")
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_used_percent = usage.percent
                disk_used_gb = usage.used / (1024 * 1024 * 1024)
                disk_total_gb = usage.total / (1024 * 1024 * 1024)
                self.logger(f"  {partition.mountpoint}: {disk_used_percent}% ({disk_used_gb:.2f}GB/{disk_total_gb:.2f}GB)")
            except (PermissionError, FileNotFoundError):
                continue
        
        self.logger("====================\n")
    
    def run(self):
        """运行恢复流程"""
        self.logger("==== 系统资源恢复开始 ====")
        
        # 显示恢复前的系统状态
        self.logger("恢复前系统状态:")
        self.show_system_status()
        
        # 停止资源占用进程
        self.stop_stresser_processes()
        
        # 清理临时文件
        self.cleanup_temp_files()
        
        # 优化系统资源
        self.optimize_system()
        
        # 等待一段时间让系统恢复
        self.logger("等待10秒让系统恢复...")
        time.sleep(10)
        
        # 显示恢复后的系统状态
        self.logger("恢复后系统状态:")
        self.show_system_status()
        
        self.logger("==== 系统资源恢复完成 ====")

if __name__ == "__main__":
    print("系统资源恢复脚本启动...")
    print("此脚本将停止所有资源占用进程并清理临时文件")
    
    # 确认用户是否要继续
    if input("是否继续? (y/n): ").lower() != 'y':
        print("操作已取消")
        sys.exit(0)
    
    recover = SystemRecover()
    recover.run()
    
    print("\n恢复完成! 详细日志请查看logs目录下的recover_*.log文件")
    input("按Enter键退出...")