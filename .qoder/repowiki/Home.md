# CloudResourceOptimizer

欢迎使用CloudResourceOptimizer！这是一个用于云主机资源利用率管理和优化的脚本工具。

## 🎯 项目简介

**CloudResourceOptimizer** 是一个智能的云主机资源利用率管理工具，能够根据云主机的规格自动调整系统资源（CPU、内存、磁盘）的利用率，使其达到监管要求的目标值。

## ✨ 主要功能

- 🔄 根据云主机内存规格自动区分小规格（≤8GB）和大规格（≥16GB）
- 📊 动态调整CPU、内存、磁盘利用率
- 📈 支持30天平均利用率统计和监控
- 📝 完整的日志记录系统
- ⚙️ 通过.env文件灵活配置各种参数
- 🖥️ 集成glances性能监控工具

## 🚀 快速开始

### Windows
```cmd
start_dynamic_redundancy.bat
```

### Linux/macOS
```bash
chmod +x start_dynamic_redundancy.sh
./start_dynamic_redundancy.sh
```

## 📚 文档导航

- [📖 使用指南](Usage-Guide) - 详细的安装和使用说明
- [🔧 API文档](API-Documentation) - 接口和函数说明
- [⚙️ 配置指南](Configuration-Guide) - 配置文件详解
- [📊 项目概述](Project-Overview) - 项目结构和架构

## 🛠️ 核心模块

### 压力测试工具
- `cpu_stresser.py` - CPU压力测试
- `memory_stresser.py` - 内存压力测试
- `disk_stresser.py` - 磁盘压力测试

### 系统管理
- `dynamic_redundancy.py` - 主控制程序
- `recover_system.py` - 系统恢复脚本

## 📞 支持与反馈

如果您在使用过程中遇到任何问题，请：

1. 查看 `logs/` 目录下的日志文件
2. 参考[故障排除指南](Usage-Guide#故障排除)
3. 在GitHub仓库提交Issue

---

> 💡 **提示**: 这个wiki内容位于 `.qoder/repowiki/` 目录，会自动同步到GitHub Wiki。
> 您可以直接编辑这些文件来更新wiki内容。