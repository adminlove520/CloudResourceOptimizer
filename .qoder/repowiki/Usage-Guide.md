# 📖 使用指南

## 🔧 安装步骤

### 1. 克隆项目
```bash
git clone https://github.com/your-username/CloudResourceOptimizer.git
cd CloudResourceOptimizer
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 运行系统

#### Windows系统
双击运行启动脚本：
```cmd
start_dynamic_redundancy.bat
```

#### Linux/macOS系统
```bash
chmod +x start_dynamic_redundancy.sh
./start_dynamic_redundancy.sh
```

## ⚙️ 配置说明

### 配置文件位置
配置文件位于 `config/.env`，包含所有系统参数设置。

### 关键配置参数

#### 内存规格定义
```ini
SMALL_MEMORY_MAX=8  # 小规格内存上限(GB)
LARGE_MEMORY_MIN=16 # 大规格内存下限(GB)
```

#### 目标利用率设置
```ini
TARGET_UTILIZATION_SMALL=25  # 小规格平均利用率目标(%)
TARGET_UTILIZATION_LARGE=40  # 大规格平均利用率目标(%)
```

#### 监控周期设置
```ini
MONITOR_PERIOD_DAYS=30        # 监控周期(天)
CHECK_INTERVAL_SECONDS=60     # 检查间隔(秒)
```

#### 工作目录配置
```ini
WORKSPACE_DIR=                # 留空使用默认路径
SCRIPT_DIR=${WORKSPACE_DIR}/scripts
LOG_DIR=${WORKSPACE_DIR}/logs
CONFIG_DIR=${WORKSPACE_DIR}/config
```

#### 磁盘监控配置
```ini
DATA_DISK_ONLY=true          # 是否只监控数据盘
DISK_STRESS_PATH=            # 磁盘占用路径(留空自动选择)
```

#### Glances监控配置
```ini
GLANCES_ENABLED=true         # 启用glances监控
GLANCES_REFRESH_INTERVAL=2   # 刷新间隔(秒)
```

### 磁盘占用控制配置

不同利用率下的文件大小和保留时间：

```ini
# 低利用率下(<30%)
LOW_UTIL_DISK_SIZE=200MB
LOW_UTIL_DURATION=3600       # 秒

# 中利用率下(30%-60%)
MED_UTIL_DISK_SIZE=100MB
MED_UTIL_DURATION=1800       # 秒

# 高利用率下(≥60%)
HIGH_UTIL_DISK_SIZE=50MB
HIGH_UTIL_DURATION=600       # 秒
```

## 📊 监控界面

### Glances Web界面
系统启动后，可通过浏览器访问监控界面：
- 默认地址：`http://localhost:61208`
- 提供实时的CPU、内存、磁盘、网络监控

### 日志查看
- 日志位置：`logs/` 目录
- 包含系统运行、错误、调试信息
- 按日期自动轮转

## 🔄 系统恢复

### 使用恢复脚本

#### Windows恢复
```cmd
# 进入恢复目录
cd Recover
# 运行恢复脚本
recover_system.bat
```

#### Linux/macOS恢复
```bash
# 进入恢复目录
cd Recover
# 赋予执行权限
chmod +x recover_system.sh
# 运行恢复脚本
./recover_system.sh
```

### 恢复功能说明
恢复脚本会执行以下操作：
1. 🛑 停止所有压力测试进程
2. 🧹 清理临时文件和缓存
3. 🔧 释放占用的系统资源
4. 📊 显示系统状态变化
5. ✅ 验证恢复结果

## 🚨 故障排除

### 常见问题及解决方案

#### 1. Glances安装问题
**问题**: 无法启动glances监控
**解决方案**: 
```bash
# 使用pip安装
pip install glances

# 或使用系统包管理器
# CentOS/RHEL
sudo yum install glances -y

# Ubuntu/Debian  
sudo apt-get install glances -y
```

#### 2. 权限问题
**问题**: 权限不足错误
**解决方案**:
- Windows: 以管理员身份运行
- Linux/macOS: 使用sudo运行或调整文件权限

#### 3. 内存调整失败
**问题**: 内存压力测试无法启动
**解决方案**:
- 检查系统可用内存
- 降低目标利用率设置
- 确认没有其他大内存消耗程序

#### 4. 磁盘空间不足
**问题**: 磁盘压力测试失败
**解决方案**:
- 检查目标磁盘可用空间
- 调整磁盘占用文件大小设置
- 更换磁盘压力测试路径

#### 5. 进程冲突
**问题**: 多个实例同时运行
**解决方案**:
```bash
# 查找相关进程
ps aux | grep dynamic_redundancy

# 终止冲突进程
kill -9 <进程ID>

# 或使用恢复脚本清理
./Recover/recover_system.sh
```

#### 6. 配置文件错误
**问题**: 配置参数无效
**解决方案**:
- 检查.env文件格式
- 确保数值参数在合理范围内
- 恢复默认配置文件

### 日志分析

#### 查看系统日志
```bash
# 查看最新日志
tail -f logs/system.log

# 查看错误日志
grep "ERROR" logs/*.log

# 查看特定时间日志
grep "2024-01-01" logs/system.log
```

#### 日志级别说明
- `DEBUG`: 详细调试信息
- `INFO`: 一般信息记录
- `WARNING`: 警告信息
- `ERROR`: 错误信息
- `CRITICAL`: 严重错误

## 📞 获取帮助

如果以上解决方案都无法解决您的问题，请：

1. **查看详细日志**: 收集 `logs/` 目录下的相关日志文件
2. **检查系统环境**: 记录操作系统版本、Python版本等信息
3. **提交Issue**: 在GitHub仓库创建Issue，包含：
   - 问题描述
   - 错误日志
   - 系统环境信息
   - 复现步骤

---

> 💡 **小贴士**: 建议在生产环境使用前，先在测试环境验证所有功能正常。