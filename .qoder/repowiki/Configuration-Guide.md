# ⚙️ 配置指南

## 系统配置

### 基本配置文件
配置文件位于 `config/` 目录下。

#### 主配置文件 (config/main.conf)
```ini
[SYSTEM]
monitor_interval = 5
log_level = INFO
enable_auto_recovery = true

[REDUNDANCY]
failover_threshold = 3
backup_count = 2
sync_interval = 10

[STRESS_TEST]
default_duration = 60
max_cpu_percentage = 80
max_memory_mb = 2048
temp_file_path = ./temp

[LOGGING]
log_directory = ./logs
max_log_size = 100MB
log_retention_days = 30
```

#### 恢复配置 (config/recovery.conf)
```ini
[RECOVERY]
auto_restart = true
restart_delay = 30
max_restart_attempts = 3
health_check_interval = 15

[NOTIFICATION]
enable_email = false
enable_slack = false
alert_threshold = CRITICAL
```

## 环境变量配置

### 必需的环境变量
```bash
# 日志级别
export LOG_LEVEL=INFO

# 工作目录
export WORK_DIR=/path/to/dynamic_redundancy

# 临时文件目录
export TEMP_DIR=/tmp/dynamic_redundancy
```

### 可选的环境变量
```bash
# 邮件通知配置
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=587
export EMAIL_USER=your-email@gmail.com
export EMAIL_PASS=your-password

# Slack通知配置
export SLACK_WEBHOOK_URL=https://hooks.slack.com/...
export SLACK_CHANNEL=#alerts
```

## 平台特定配置

### Windows配置
- 确保PowerShell执行策略允许脚本运行
- 配置Windows服务（可选）
- 设置防火墙规则

### Linux/macOS配置
- 设置适当的文件权限
- 配置systemd服务（Linux）
- 设置cron任务（可选）

## 高级配置

### 集群模式配置
```ini
[CLUSTER]
enable_cluster = true
node_id = node-1
cluster_nodes = node-1:192.168.1.10,node-2:192.168.1.11
sync_port = 8080
```

### 监控配置
```ini
[MONITORING]
enable_metrics = true
metrics_port = 9090
health_check_endpoint = /health
status_endpoint = /status
```

## 故障排除

### 常见配置问题
1. **权限问题**: 确保日志和配置目录有写权限
2. **端口冲突**: 检查配置的端口是否被占用
3. **路径问题**: 确保所有路径都是绝对路径或正确的相对路径

### 配置验证
运行配置验证命令：
```bash
python scripts/validate_config.py
```