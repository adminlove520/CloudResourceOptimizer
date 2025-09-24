# CloudResourceOptimizer

## 项目简介

**CloudResourceOptimizer**是一个用于云主机资源利用率管理和优化的脚本工具，能够根据云主机的规格（特别是内存大小）自动调整系统资源（CPU、内存、磁盘）的利用率，使其达到监管云要求的目标值。本工具通过智能调控系统资源占用，实现云主机资源的高效利用和优化管理。

主要功能：
- 根据云主机内存规格自动区分小规格（≤8GB）和大规格（≥16GB）
- 动态调整CPU、内存、磁盘利用率，小规格达到25%以上，大规格达到40%左右
- 支持30天平均利用率统计和监控
- 完整的日志记录系统
- 可通过.env文件灵活配置各种参数
- 集成glances性能监控工具

## 项目结构

```
CloudResourceOptimizer/
├── requirements.txt              # Python依赖包
├── README.md                     # 项目说明文档
├── scripts/                      # 脚本目录
│   ├── dynamic_redundancy.py     # 主控制脚本
│   ├── memory_stresser.py        # 内存占用工具
│   ├── disk_stresser.py          # 磁盘占用工具
│   └── cpu_stresser.py           # CPU占用工具
├── logs/                         # 日志目录
├── config/                       # 配置文件目录
│   └── .env                      # 环境配置文件
├── Recover/                      # 恢复脚本目录
│   ├── recover_system.bat        # Windows恢复脚本
│   ├── recover_system.py         # 系统恢复主脚本
│   └── recover_system.sh         # Linux恢复脚本
├── start_dynamic_redundancy.bat  # Windows启动脚本
└── start_dynamic_redundancy.sh   # Linux启动脚本
```

## 环境要求

- Python 3.6+ 
- 操作系统：Windows/Linux

## 安装依赖

使用pip安装所需依赖：

```bash
pip install -r requirements.txt
```

## 配置说明

通过修改`config`目录下的`.env`文件来配置脚本行为：

```ini
# CloudResourceOptimizer 环境配置文件
# 此文件位于 config 目录下
# 内存规格定义
SMALL_MEMORY_MAX=8  # 小规格内存上限(GB)
LARGE_MEMORY_MIN=16 # 大规格内存下限(GB)

# 目标利用率设置（百分比）
TARGET_UTILIZATION_SMALL=25  # 小规格平均利用率目标
TARGET_UTILIZATION_LARGE=40  # 大规格平均利用率目标

# 监控周期设置
MONITOR_PERIOD_DAYS=30  # 监控周期(天)
CHECK_INTERVAL_SECONDS=60  # 检查间隔(秒)

# 工作区配置
# 留空则使用脚本所在目录的父目录作为工作区目录（推荐使用相对路径）
WORKSPACE_DIR=
SCRIPT_DIR=${WORKSPACE_DIR}/scripts
LOG_DIR=${WORKSPACE_DIR}/logs
CONFIG_DIR=${WORKSPACE_DIR}/config

# 磁盘监控配置
DATA_DISK_ONLY=true  # 是否只监控数据盘

# 平台配置
# 支持的平台：auto, centos, ubuntu, kylin, openEuler
# auto: 自动检测系统类型
PLATFORM=auto

# glances监控配置
GLANCES_ENABLED=true
GLANCES_REFRESH_INTERVAL=2

# 磁盘占用控制配置
# 磁盘占用默认路径（留空则使用最大的目录路径）
DISK_STRESS_PATH=

# 低利用率下的文件大小和保留时间（利用率<30%）
LOW_UTIL_DISK_SIZE=200MB
LOW_UTIL_DURATION=3600  # 秒

# 中利用率下的文件大小和保留时间（30%≤利用率<60%）
MED_UTIL_DISK_SIZE=100MB
MED_UTIL_DURATION=1800  # 秒

# 高利用率下的文件大小和保留时间（利用率≥60%）
HIGH_UTIL_DISK_SIZE=50MB
HIGH_UTIL_DURATION=600  # 秒
```

## 使用方法

1. 安装依赖包
2. 根据需要修改`.env`配置文件
3. 运行主脚本：

```bash
python scripts/dynamic_redundancy.py
```

## 恢复脚本使用方法

项目包含完整的系统资源恢复工具，位于Recover目录下：

### Windows系统
1. 双击运行 `Recover\recover_system.bat`
2. 按照提示确认操作
3. 等待恢复过程完成

### Linux系统
1. 打开终端并切换到Recover目录
2. 执行命令：`./recover_system.sh`
3. 按照提示确认操作
4. 等待恢复过程完成

恢复脚本会：
- 停止所有资源占用进程（CPU、内存、磁盘占用脚本）
- 清理临时文件
- 优化系统资源
- 显示系统状态变化

### 注意事项
1. 如需要恢复系统资源，可随时运行Recover目录下的恢复脚本

## 功能模块说明

### 1. 配置管理模块（ConfigManager）
负责读取和解析.env配置文件，提供全局配置访问接口。

### 2. 日志管理模块（Logger）
负责记录系统运行日志，包括信息、警告和错误日志，同时输出到文件和控制台。

### 3. 系统监控模块（SystemMonitor）
- 检测云主机规格（小规格或大规格）
- 收集CPU、内存、磁盘的实时利用率和平均利用率
- 维护资源使用历史数据

### 4. 冗余控制模块（RedundancyController）
- 根据系统规格和当前资源使用情况，动态调整CPU、内存、磁盘利用率
- 对于内存：创建内存占用进程
- 对于CPU：创建CPU密集型任务
- 对于磁盘：在数据盘创建临时大文件

### 5. Glances监控模块（GlancesMonitor）
集成glances工具，提供Web界面的实时性能监控。

## 注意事项

1. 脚本需要以管理员/root权限运行，特别是在调整系统资源和创建大文件时
2. 临时文件会根据配置的保留时间自动删除，避免永久占用磁盘空间
3. 监控历史数据会根据配置的监控周期自动清理，避免内存占用过大
4. 在Windows系统上，某些操作可能需要额外的权限

## 扩展说明

如果需要扩展功能，可以考虑：
- 添加更多资源类型的监控和调整
- 实现基于网络流量的冗余控制
- 开发Web管理界面
- 增加告警机制

## GitHub Actions 自动化

项目集成了GitHub Actions工作流，提供以下自动化功能：

### Wiki自动同步
- **自动触发**：当推送到main/master分支时，自动同步wiki内容
- **手动同步**：在Actions页面可手动触发wiki同步
- **内容同步**：自动将README.md、wiki/和docs/目录内容同步到GitHub Wiki

### 使用方法

1. **自动同步**：推送代码到main分支即可自动触发
2. **手动同步**：
   - 访问GitHub仓库的Actions页面
   - 选择"Manual Wiki Sync"工作流
   - 点击"Run workflow"按钮
   - 选择同步类型（完整/增量）和是否强制更新

### Wiki文档结构
- **Home**: 项目主页（来自README.md）
- **Project-Overview**: 项目概述和结构说明
- **Usage-Guide**: 详细使用指南
- **API-Documentation**: API接口文档
- **Configuration-Guide**: 配置指南
- **Project-Statistics**: 项目统计信息

## 文档和Wiki

项目提供完整的文档支持：

- **在线Wiki**: [GitHub Wiki页面](../../wiki) - 包含详细的使用指南和API文档
- **本地文档**: `.qoder/repowiki/`目录包含所有文档源文件
- **自动同步**: 文档更改会自动同步到GitHub Wiki

### Wiki管理工具
使用内置的wiki管理工具：

```bash
# 列出wiki文件
python scripts/wiki_manager.py list

# 创建新的wiki文件
python scripts/wiki_manager.py create "新页面名称"

# 查看同步方法
python scripts/wiki_manager.py sync

# 备份wiki内容
python scripts/wiki_manager.py backup
```

### Wiki内容结构
- **Home.md**: 项目主页和导航
- **Usage-Guide.md**: 详细使用指南
- **Project-Overview.md**: 项目概述和架构
- **API-Documentation.md**: API接口文档
- **Configuration-Guide.md**: 配置指南

## 故障排除

1. **无法启动glances监控**：检查是否安装了glances，或手动运行`pip install glances `
2. **无法安装glances**：手动运行`sudo yum install glances -y` 或 `sudo apt-get install glances`
3. **权限错误**：确保以管理员/root权限运行脚本
4. **内存调整失败**：检查系统内存是否充足，以及是否有足够的权限
5. **磁盘空间不足**：如果磁盘空间不足，脚本会自动跳过磁盘调整操作
6. **Wiki同步失败**：检查GitHub Actions日志，确认仓库有Wiki功能开启