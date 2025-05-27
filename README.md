# 域名到期提醒日历生成器

这个项目用于自动生成域名和 SSL 证书到期提醒的日历文件。它会读取 YAML 配置文件中的域名信息，并生成一个包含到期提醒的 ICS 日历文件，可以导入到各种日历应用中。

## 功能特点

- 支持域名到期提醒
- 支持 SSL 证书到期提醒
- 自动生成提前 7 天的提醒
- 生成标准的 ICS 日历文件
- 使用中国时区（Asia/Shanghai）

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

在 `work_management.yaml` 文件中配置域名信息，格式如下：

```yaml
domains_expiry:
  example.com: '2025-06-14'
  example.org: '2025-06-14'
domains_ssl_expiry:
  example.com: '2025-06-17'
  example.org: '2025-06-17'
```

## 使用方法

1. 确保 `work_management.yaml` 文件已正确配置

2. 运行脚本生成日历文件：
```bash
python generate_calendar.py
```

3. 脚本会生成 `domain_expiry_calendar.ics` 文件

4. 将生成的 ICS 文件导入到你的日历应用中：
   - Google Calendar
   - Apple Calendar
   - Microsoft Outlook
   - 其他支持 ICS 格式的日历应用

## 日历事件说明

对于每个域名和 SSL 证书，会生成两个提醒事件：
1. 到期前 7 天的提醒
2. 到期当天的提醒

## 注意事项

- 确保 YAML 文件中的日期格式为 'YYYY-MM-DD'
- 生成的日历文件使用中国时区
- 所有提醒事件都设置为全天事件

## 依赖包

- pyyaml: 用于读取 YAML 配置文件
- icalendar: 用于生成 ICS 日历文件
- pytz: 用于处理时区 