# 日程自动化管理系统

这个项目用于自动化管理各类日程提醒，包括但不限于域名到期、证书到期、工作安排、个人事项等。通过统一的配置和自动化流程，帮助用户更好地管理各类重要时间节点。

## 功能模块

### 1. 域名管理模块
- 域名到期提醒
- SSL证书到期提醒
- 自动生成日历事件
- 提前7天提醒功能

### 2. 工作管理模块（待建）
- 项目截止日期提醒
- 会议安排提醒
- 任务截止日期提醒

### 3. 个人管理模块（待建）
- 重要日期提醒
- 纪念日提醒
- 个人待办事项提醒

## 系统特点

- 支持多种提醒类型
- 自动生成标准 ICS 日历文件
- 支持提前提醒功能
- 使用中国时区（Asia/Shanghai）
- 自动化检查和更新
- 支持 GitHub Actions 自动运行

## 安装要求

- Python 3.6 或更高版本
- 必要的 Python 包（见 requirements.txt）

## 安装步骤

1. 克隆或下载本项目到本地

2. 安装依赖包：
```bash
pip install -r requirements.txt
```

## 配置文件

项目使用 YAML 格式的配置文件来管理各类提醒事项。每个模块都有其对应的配置文件：

### 域名管理配置 (domain_expiry.yaml)
```yaml
domains_expiry:
  example.com: '2025-06-14'
  example.org: '2025-06-14'
domains_ssl_expiry:
  example.com: '2025-06-17'
  example.org: '2025-06-17'
```

### 工作管理配置 (work_management.yaml)
```yaml
project_deadlines:
  project1: '2024-12-31'
  project2: '2024-12-31'
meetings:
  weekly_meeting: '2024-12-31'
tasks:
  task1: '2024-12-31'
```

### 个人管理配置 (personal_management.yaml)
```yaml
important_dates:
  birthday: '2024-12-31'
  anniversary: '2024-12-31'
todos:
  task1: '2024-12-31'
```

## 使用方法

1. 配置相应的 YAML 文件

2. 运行对应的脚本生成日历文件：
```bash
# 域名管理
python domain_expiry/generate_calendar.py

# 工作管理
python work_management/generate_calendar.py

# 个人管理
python personal_management/generate_calendar.py
```

3. 将生成的 ICS 文件导入到你的日历应用中：
   - Google Calendar
   - Apple Calendar
   - Microsoft Outlook
   - 其他支持 ICS 格式的日历应用

## 自动化运行

项目使用 GitHub Actions 实现自动化运行：

- 每天自动检查域名和证书状态
- 自动更新配置文件
- 自动生成最新的日历文件
- 自动提交更改

## 注意事项

- 确保 YAML 文件中的日期格式为 'YYYY-MM-DD'
- 生成的日历文件使用中国时区
- 所有提醒事件都设置为全天事件
- 定期检查配置文件确保信息准确

## 依赖包

- pyyaml: 用于读取 YAML 配置文件
- icalendar: 用于生成 ICS 日历文件
- pytz: 用于处理时区
- python-whois: 用于检查域名信息
- pyOpenSSL: 用于检查 SSL 证书
- dnspython: 用于 DNS 记录检查
- requests: 用于网站状态检查 