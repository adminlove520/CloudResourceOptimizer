#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CloudResourceOptimizer
用于根据云主机规格动态调整系统资源利用率，使内存、CPU、磁盘利用率达到目标值
"""

import os
import sys
import re
import time
import psutil
import logging
import platform
import threading
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# 全局变量
resource_history = {
    'cpu': [],
    'memory': [],
    'disk': []
}

class ConfigManager:
    """配置管理类，负责读取和解析.env配置文件"""
    def __init__(self):
        self.config = {}
        self.load_config()
        
    def load_config(self):
        """加载.env配置文件"""
        try:
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', '.env')
            load_dotenv(dotenv_path=env_path)
            
            # 内存规格定义
            self.config['SMALL_MEMORY_MAX'] = int(os.getenv('SMALL_MEMORY_MAX', 8))
            self.config['LARGE_MEMORY_MIN'] = int(os.getenv('LARGE_MEMORY_MIN', 16))
            
            # 目标利用率设置
            self.config['TARGET_UTILIZATION_SMALL'] = int(os.getenv('TARGET_UTILIZATION_SMALL', 25))
            self.config['TARGET_UTILIZATION_LARGE'] = int(os.getenv('TARGET_UTILIZATION_LARGE', 40))
            
            # 监控周期设置
            self.config['MONITOR_PERIOD_DAYS'] = int(os.getenv('MONITOR_PERIOD_DAYS', 30))
            self.config['CHECK_INTERVAL_SECONDS'] = int(os.getenv('CHECK_INTERVAL_SECONDS', 60))
            
            # 工作区配置
            workspace_dir = os.getenv('WORKSPACE_DIR', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.config['WORKSPACE_DIR'] = workspace_dir
            self.config['SCRIPT_DIR'] = os.getenv('SCRIPT_DIR', os.path.join(workspace_dir, 'scripts'))
            self.config['LOG_DIR'] = os.getenv('LOG_DIR', os.path.join(workspace_dir, 'logs'))
            self.config['CONFIG_DIR'] = os.getenv('CONFIG_DIR', os.path.join(workspace_dir, 'config'))
            
            # 磁盘监控配置
            self.config['DATA_DISK_ONLY'] = os.getenv('DATA_DISK_ONLY', 'true').lower() == 'true'
            
            # glances监控配置
            self.config['GLANCES_ENABLED'] = os.getenv('GLANCES_ENABLED', 'true').lower() == 'true'
            self.config['GLANCES_REFRESH_INTERVAL'] = int(os.getenv('GLANCES_REFRESH_INTERVAL', 2))
            
            # 平台配置
            self.config['PLATFORM'] = os.getenv('PLATFORM', 'auto').lower()
            
            # 磁盘占用控制配置
            self.config['DISK_STRESS_PATH'] = os.getenv('DISK_STRESS_PATH', '')
            self.config['LOW_UTIL_DISK_SIZE'] = os.getenv('LOW_UTIL_DISK_SIZE', '200MB')
            self.config['LOW_UTIL_DURATION'] = int(os.getenv('LOW_UTIL_DURATION', '3600'))
            self.config['MED_UTIL_DISK_SIZE'] = os.getenv('MED_UTIL_DISK_SIZE', '100MB')
            self.config['MED_UTIL_DURATION'] = int(os.getenv('MED_UTIL_DURATION', '1800'))
            self.config['HIGH_UTIL_DISK_SIZE'] = os.getenv('HIGH_UTIL_DISK_SIZE', '50MB')
            self.config['HIGH_UTIL_DURATION'] = int(os.getenv('HIGH_UTIL_DURATION', '600'))
            
        except Exception as e:
            logging.error(f"配置文件加载失败: {e}")
            # 使用默认配置
            self.config = {
                'SMALL_MEMORY_MAX': 8,
                'LARGE_MEMORY_MIN': 16,
                'TARGET_UTILIZATION_SMALL': 25,
                'TARGET_UTILIZATION_LARGE': 40,
                'MONITOR_PERIOD_DAYS': 30,
                'CHECK_INTERVAL_SECONDS': 60,
                'WORKSPACE_DIR': os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'SCRIPT_DIR': os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'),
                'LOG_DIR': os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs'),
                'CONFIG_DIR': os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config'),
                'DATA_DISK_ONLY': True,
                'GLANCES_ENABLED': True,
                'GLANCES_REFRESH_INTERVAL': 2,
                'PLATFORM': 'auto',
                'DISK_STRESS_PATH': '',
                'LOW_UTIL_DISK_SIZE': '200MB',
                'LOW_UTIL_DURATION': 3600,
                'MED_UTIL_DISK_SIZE': '100MB',
                'MED_UTIL_DURATION': 1800,
                'HIGH_UTIL_DISK_SIZE': '50MB',
                'HIGH_UTIL_DURATION': 600
            }
    
    def get(self, key, default=None):
        """获取配置项的值"""
        return self.config.get(key, default)

class Logger:
    """日志管理类，负责配置和记录日志"""
    def __init__(self, log_dir):
        # 确保日志目录存在
        os.makedirs(log_dir, exist_ok=True)
        
        # 日志文件路径
        log_file = os.path.join(log_dir, f"cloud_resource_optimizer_{datetime.now().strftime('%Y%m%d')}.log")
        
        # 配置日志格式
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('cloud_resource_optimizer')
    
    def info(self, message):
        """记录信息日志"""
        self.logger.info(message)
    
    def warning(self, message):
        """记录警告日志"""
        self.logger.warning(message)
    
    def error(self, message):
        """记录错误日志"""
        self.logger.error(message)
    
    def debug(self, message):
        """记录调试日志"""
        self.logger.debug(message)

class SystemMonitor:
    """系统监控类，负责收集系统资源使用情况"""
    def __init__(self, config_manager, logger):
        self.config = config_manager
        self.logger = logger
        self.system_spec = self.detect_system_spec()
    
    def detect_system_spec(self):
        """检测系统规格，返回'small'或'large'"""
        try:
            # 获取总内存(GB)
            total_memory = psutil.virtual_memory().total / (1024 ** 3)
            
            if total_memory <= self.config.get('SMALL_MEMORY_MAX'):
                return 'small'
            elif total_memory >= self.config.get('LARGE_MEMORY_MIN'):
                return 'large'
            else:
                # 介于8-16之间的，暂时归为small
                return 'small'
        except Exception as e:
            self.logger.error(f"系统规格检测失败: {e}")
            return 'small'
    
    def get_system_info(self):
        """获取系统基本信息"""
        try:
            info = {
                'platform': platform.platform(),
                'processor': platform.processor(),
                'memory_total_gb': round(psutil.virtual_memory().total / (1024 ** 3), 2),
                'cpu_count': psutil.cpu_count(logical=True),
                'disk_count': len(psutil.disk_partitions(all=not self.config.get('DATA_DISK_ONLY')))
            }
            return info
        except Exception as e:
            self.logger.error(f"系统信息获取失败: {e}")
            return {}
    
    def get_resource_usage(self):
        """获取当前系统资源使用情况"""
        try:
            # CPU使用率
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # 磁盘使用率
            disk_usage = 0
            disk_count = 0
            
            for partition in psutil.disk_partitions(all=not self.config.get('DATA_DISK_ONLY')):
                try:
                    # 跳过一些特殊的文件系统
                    if partition.fstype in ['', 'sysfs', 'proc', 'devtmpfs', 'tmpfs', 'devpts', 'cgroup', 'pstore']:
                        continue
                    
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage += usage.percent
                    disk_count += 1
                except (PermissionError, FileNotFoundError):
                    continue
            
            # 计算平均磁盘使用率
            if disk_count > 0:
                disk_usage = disk_usage / disk_count
            
            # 记录历史数据
            global resource_history
            resource_history['cpu'].append(cpu_usage)
            resource_history['memory'].append(memory_usage)
            resource_history['disk'].append(disk_usage)
            
            # 保持历史数据不超过监控周期
            max_history = (self.config.get('MONITOR_PERIOD_DAYS') * 24 * 3600) // self.config.get('CHECK_INTERVAL_SECONDS')
            for key in resource_history:
                if len(resource_history[key]) > max_history:
                    resource_history[key] = resource_history[key][-max_history:]
            
            return {
                'cpu': cpu_usage,
                'memory': memory_usage,
                'disk': disk_usage,
                'cpu_avg': sum(resource_history['cpu']) / len(resource_history['cpu']) if resource_history['cpu'] else 0,
                'memory_avg': sum(resource_history['memory']) / len(resource_history['memory']) if resource_history['memory'] else 0,
                'disk_avg': sum(resource_history['disk']) / len(resource_history['disk']) if resource_history['disk'] else 0
            }
        except Exception as e:
            self.logger.error(f"资源使用情况获取失败: {e}")
            return {
                'cpu': 0,
                'memory': 0,
                'disk': 0,
                'cpu_avg': 0,
                'memory_avg': 0,
                'disk_avg': 0
            }

class RedundancyController:
    """冗余控制类，负责动态调整系统资源利用率"""
    def __init__(self, config_manager, logger, system_monitor):
        self.config = config_manager
        self.logger = logger
        self.system_monitor = system_monitor
        self.system_spec = system_monitor.system_spec
        
        # 根据系统规格设置目标利用率
        if self.system_spec == 'small':
            self.target_utilization = self.config.get('TARGET_UTILIZATION_SMALL')
        else:
            self.target_utilization = self.config.get('TARGET_UTILIZATION_LARGE')
        
        self.logger.info(f"系统规格: {self.system_spec}, 目标利用率: {self.target_utilization}%")
    
    def adjust_memory_usage(self, current_usage, current_avg_usage):
        """调整内存使用率"""
        try:
            # 计算需要增加的内存使用量
            memory = psutil.virtual_memory()
            total_memory = memory.total
            
            # 如果平均使用率低于目标，增加内存使用
            if current_avg_usage < self.target_utilization:
                # 需要达到的内存使用量
                required_usage_percent = min(self.target_utilization + 5, 90)  # 最多使用90%
                required_used_memory = total_memory * required_usage_percent / 100
                memory_to_use = required_used_memory - memory.used
                
                if memory_to_use > 0:
                    # 转换为MB
                    memory_to_use_mb = memory_to_use / (1024 * 1024)
                    
                    # 如果需要使用的内存超过1GB，限制为1GB
                    memory_to_use_mb = min(memory_to_use_mb, 1024)
                    
                    self.logger.info(f"增加内存使用: {memory_to_use_mb:.2f} MB")
                    
                    # 创建内存占用进程
                    mem_script = os.path.join(self.config.get('SCRIPT_DIR'), 'memory_stresser.py')
                    if os.path.exists(mem_script):
                        subprocess.Popen([sys.executable, mem_script, f"{int(memory_to_use_mb)}MB"])
                    else:
                        # 如果没有专门的内存占用脚本，创建一个临时的
                        self._create_memory_load(memory_to_use_mb)
        except Exception as e:
            self.logger.error(f"内存调整失败: {e}")
    
    def _create_memory_load(self, mb):
        """创建内存负载"""
        try:
            # 在当前进程中分配内存
            # 注意：这只是一个简单的实现，在实际生产环境中应该使用单独的进程
            load = ' ' * int(mb * 1024 * 1024)  # 1MB = 1,048,576 bytes
            time.sleep(60)  # 保持内存占用60秒
        except Exception as e:
            self.logger.error(f"创建内存负载失败: {e}")
    
    def adjust_cpu_usage(self, current_usage, current_avg_usage):
        """调整CPU使用率"""
        try:
            # 如果平均使用率低于目标，增加CPU使用
            if current_avg_usage < self.target_utilization:
                self.logger.info("增加CPU使用")
                
                # 创建CPU占用进程
                cpu_script = os.path.join(self.config.get('SCRIPT_DIR'), 'cpu_stresser.py')
                if os.path.exists(cpu_script):
                    subprocess.Popen([sys.executable, cpu_script])
                else:
                    # 创建临时线程来占用CPU
                    threading.Thread(target=self._create_cpu_load, daemon=True).start()
        except Exception as e:
            self.logger.error(f"CPU调整失败: {e}")
    
    def _create_cpu_load(self):
        """创建CPU负载"""
        try:
            # 占用CPU一段时间
            end_time = time.time() + 60  # 持续60秒
            while time.time() < end_time:
                _ = [i * i for i in range(10000)]
        except Exception as e:
            self.logger.error(f"创建CPU负载失败: {e}")
    
    def detect_platform(self):
        """检测操作系统平台"""
        # 从配置中获取平台设置
        platform_config = self.config.get('PLATFORM', 'auto').lower()
        
        if platform_config != 'auto':
            self.logger.info(f"使用配置的平台: {platform_config}")
            return platform_config
        
        # 自动检测平台
        system = platform.system().lower()
        if system == 'windows':
            return 'windows'
        elif system == 'linux':
            # 尝试检测Linux发行版
            try:
                with open('/etc/os-release', 'r') as f:
                    content = f.read().lower()
                    if 'centos' in content:
                        return 'centos'
                    elif 'ubuntu' in content:
                        return 'ubuntu'
                    elif 'kylin' in content:
                        return 'kylin'
                    elif 'openEuler' in content or 'openeuler' in content:
                        return 'openEuler'
                    else:
                        self.logger.warning("无法识别的Linux发行版，使用通用配置")
                        return 'linux_generic'
            except Exception as e:
                self.logger.error(f"检测Linux发行版失败: {e}")
                return 'linux_generic'
        else:
            self.logger.warning(f"未知操作系统: {system}")
            return 'unknown'
    
    def adjust_disk_usage(self, current_usage, current_avg_usage):
        """调整磁盘使用率"""
        try:
            # 如果平均使用率低于目标，增加磁盘使用
            if current_avg_usage < self.target_utilization:
                # 检测当前平台
                current_platform = self.detect_platform()
                
                # 获取配置的磁盘路径
                disk_stress_path = self.config.get('DISK_STRESS_PATH', '')
                disk_path = None
                
                # 如果配置了磁盘路径且有效，则使用配置的路径
                if disk_stress_path and os.path.exists(disk_stress_path):
                    # 检查配置路径是否有足够空间
                    try:
                        usage = psutil.disk_usage(disk_stress_path)
                        if usage.free > 1024 * 1024 * 1024:  # 至少1GB空闲空间
                            disk_path = disk_stress_path
                        else:
                            self.logger.warning(f"配置的磁盘路径 {disk_stress_path} 空间不足")
                    except Exception as e:
                        self.logger.error(f"检查配置路径失败: {e}")
                
                # 如果没有配置有效路径或配置路径不可用，则寻找合适的数据盘
                if not disk_path:
                    # 寻找合适的数据盘
                    data_disks = []
                    disk_sizes = []
                    
                    for partition in psutil.disk_partitions(all=not self.config.get('DATA_DISK_ONLY')):
                        try:
                            # 跳过系统盘
                            if self.config.get('DATA_DISK_ONLY'):
                                if current_platform == 'windows':
                                    if partition.mountpoint.lower() == 'c:':
                                        continue
                                else:
                                    # 对于Linux系统，跳过根目录和常见的系统挂载点
                                    system_mounts = ['/', '/boot', '/boot/efi', '/sys', '/proc', '/dev']
                                    if partition.mountpoint in system_mounts:
                                        continue
                        
                            usage = psutil.disk_usage(partition.mountpoint)
                            # 确保有足够空间
                            if usage.free > 1024 * 1024 * 1024:  # 至少1GB空闲空间
                                data_disks.append(partition.mountpoint)
                                disk_sizes.append(usage.total)  # 记录磁盘总大小
                        except (PermissionError, FileNotFoundError):
                            continue
                    
                    if data_disks:
                        # 选择最大的磁盘
                        largest_disk_index = disk_sizes.index(max(disk_sizes))
                        disk_path = data_disks[largest_disk_index]
                
                if disk_path:
                    # 根据当前利用率选择文件大小和保留时间
                    if current_avg_usage < 30:
                        # 低利用率
                        file_size = self.config.get('LOW_UTIL_DISK_SIZE', '200MB')
                        duration_seconds = self.config.get('LOW_UTIL_DURATION', 3600)
                    elif current_avg_usage < 60:
                        # 中利用率
                        file_size = self.config.get('MED_UTIL_DISK_SIZE', '100MB')
                        duration_seconds = self.config.get('MED_UTIL_DURATION', 1800)
                    else:
                        # 高利用率
                        file_size = self.config.get('HIGH_UTIL_DISK_SIZE', '50MB')
                        duration_seconds = self.config.get('HIGH_UTIL_DURATION', 600)
                    
                    self.logger.info(f"在 {disk_path} 创建 {file_size} 的临时文件，保留 {duration_seconds} 秒")
                    
                    # 使用disk_stresser.py脚本
                    disk_script = os.path.join(self.config.get('SCRIPT_DIR'), 'disk_stresser.py')
                    if os.path.exists(disk_script):
                        # 根据平台调整命令格式
                        if current_platform == 'windows':
                            # Windows平台
                            cmd = [
                                sys.executable,
                                disk_script,
                                '--path', disk_path,
                                '--size', file_size,
                                '--duration', str(duration_seconds)
                            ]
                        else:
                            # Linux平台
                            cmd = [
                                'python3',
                                disk_script,
                                '--path', disk_path,
                                '--size', file_size,
                                '--duration', str(duration_seconds)
                            ]
                        
                        try:
                            subprocess.Popen(cmd)
                            self.logger.info(f"已启动磁盘占用脚本，平台: {current_platform}")
                        except Exception as e:
                            self.logger.error(f"启动磁盘占用脚本失败: {e}")
                    else:
                        self.logger.error(f"磁盘占用脚本不存在: {disk_script}")
        except Exception as e:
            self.logger.error(f"磁盘调整失败: {e}")
    
    def run(self):
        """运行冗余控制逻辑"""
        try:
            # 获取当前资源使用情况
            resource_usage = self.system_monitor.get_resource_usage()
            
            self.logger.info(f"当前资源使用情况 - CPU: {resource_usage['cpu']:.2f}% (平均: {resource_usage['cpu_avg']:.2f}%), "
                            f"内存: {resource_usage['memory']:.2f}% (平均: {resource_usage['memory_avg']:.2f}%), "
                            f"磁盘: {resource_usage['disk']:.2f}% (平均: {resource_usage['disk_avg']:.2f}%)")
            
            # 调整各资源使用率
            self.adjust_memory_usage(resource_usage['memory'], resource_usage['memory_avg'])
            self.adjust_cpu_usage(resource_usage['cpu'], resource_usage['cpu_avg'])
            self.adjust_disk_usage(resource_usage['disk'], resource_usage['disk_avg'])
        except Exception as e:
            self.logger.error(f"冗余控制执行失败: {e}")

class GlancesMonitor:
    """Glances监控类，用于启动和管理glances监控"""
    def __init__(self, config_manager, logger):
        self.config = config_manager
        self.logger = logger
        self.process = None
    
    def start(self):
        """启动glances监控"""
        try:
            if self.config.get('GLANCES_ENABLED'):
                # 检查glances是否安装
                try:
                    subprocess.run(['glances', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    self.logger.info("启动glances监控")
                    
                    # 启动glances服务模式
                    self.process = subprocess.Popen([
                        'glances', 
                        '--webserver', 
                        '--port', '61208',
                        '--refresh', str(self.config.get('GLANCES_REFRESH_INTERVAL'))
                    ])
                except subprocess.CalledProcessError:
                    self.logger.warning("未安装glances，无法启动监控服务")
                    # 尝试安装glances
                    try:
                        self.logger.info("正在尝试安装glances")
                        subprocess.run([sys.executable, '-m', 'pip', 'install', 'glances'], check=True)
                        self.logger.info("glances安装成功")
                        self.start()  # 重新启动
                    except Exception as e:
                        self.logger.error(f"glances安装失败: {e}")
        except Exception as e:
            self.logger.error(f"启动glances失败: {e}")
    
    def stop(self):
        """停止glances监控"""
        try:
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=5)
                self.logger.info("已停止glances监控")
        except Exception as e:
            self.logger.error(f"停止glances失败: {e}")

def create_memory_stresser_script(script_dir):
    """创建内存占用脚本"""
    script_path = os.path.join(script_dir, 'memory_stresser.py')
    content = '''#!/usr/bin/env python3
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
'''
    
    try:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 添加可执行权限
        if platform.system() != 'Windows':
            os.chmod(script_path, 0o755)
        
        return True
    except Exception as e:
        print(f"创建内存占用脚本失败: {e}")
        return False


def create_cpu_stresser_script(script_dir):
    """创建CPU占用脚本"""
    script_path = os.path.join(script_dir, 'cpu_stresser.py')
    content = '''#!/usr/bin/env python3
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
'''
    
    try:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 添加可执行权限
        if platform.system() != 'Windows':
            os.chmod(script_path, 0o755)
        
        return True
    except Exception as e:
        print(f"创建CPU占用脚本失败: {e}")
        return False


def main():
    """主函数"""
    try:
        # 加载配置
        config_manager = ConfigManager()
        
        # 初始化日志
        logger = Logger(config_manager.get('LOG_DIR'))
        
        # 记录启动信息
        logger.info("CloudResourceOptimizer启动")
        
        # 创建必要的工具脚本
        create_memory_stresser_script(config_manager.get('SCRIPT_DIR'))
        create_cpu_stresser_script(config_manager.get('SCRIPT_DIR'))
        
        # 初始化系统监控
        system_monitor = SystemMonitor(config_manager, logger)
        
        # 记录系统信息
        system_info = system_monitor.get_system_info()
        logger.info(f"系统信息: {system_info}")
        
        # 初始化冗余控制器
        redundancy_controller = RedundancyController(config_manager, logger, system_monitor)
        
        # 启动glances监控
        glances_monitor = GlancesMonitor(config_manager, logger)
        glances_monitor.start()
        
        # 主循环
        try:
            while True:
                redundancy_controller.run()
                time.sleep(config_manager.get('CHECK_INTERVAL_SECONDS'))
        except KeyboardInterrupt:
            logger.info("收到中断信号，正在停止服务...")
        finally:
            # 停止glances监控
            glances_monitor.stop()
            
    except Exception as e:
        print(f"程序运行失败: {e}")
        sys.exit(1)
    
    logger.info("CloudResourceOptimizer已停止")
    sys.exit(0)


if __name__ == "__main__":
    main()