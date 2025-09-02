# 日程自动化管理系统

用于自动化管理各类日程提醒：域名到期、SSL 证书到期、以及订阅服务等。通过统一配置与自动化流程，帮助你及时跟进重要时间节点。

## 功能模块

* __域名管理__：
  - 域名到期提醒（按天）
  - SSL 证书到期提醒（支持含协议/端口的目标，如 `https://host:port`）
  - 自动生成 ICS 日历，包含“到期当天事件 + 提前 7 天提醒事件”

* __订阅服务__：
  - 订阅到期提醒、费用展示、分类聚合
  - 前端表格高亮将到期状态与剩余/超期天数

* __前端仪表盘__：
  - 页面：`index.html`
  - 模块拆分：域名到期、证书到期、订阅服务独立展示
  - 失败兜底：数据加载失败时分别对各表格展示错误行

## 系统特点

* __标准 ICS__：自动生成标准 ICS 文件
* __提前提醒__：默认提前 7 天事件
* __中国时区__：Asia/Shanghai
* __自动化__：支持 GitHub Actions 定时执行（见 `.github/workflows/schedule_automation.yml`）

## 环境要求

* __Python__：3.8 或更高版本（建议）
* __依赖__：见 `requirements.txt`

## 快速开始

1) 安装依赖
```bash
pip install -r requirements.txt
```

2) 配置 YAML

位于 `domain_expiry/domain_expiry.yaml`：
```yaml
domains_expiry:
  example.com: '2026-06-14'
  example.org: '2027-05-18'
domains_ssl_expiry:
  https://example.com: null
  https://example.org: '2025-10-22'
```

位于 `subscription_services/subscription_services.yaml`：
```yaml
subscription_services:
  jd_2025:
    name: 京东PLUS
    expiry_date: '2026-03-05'
    cost: 99.0
    status: 订阅中
    category: 购物
```

3) 生成 ICS 文件
```bash
# 域名与证书到期 ICS（输出：domain_expiry/domain_expiry_calendar.ics）
python domain_expiry/generate_domain_calendar.py

# 订阅服务 ICS（输出：subscription_services/subscription_services_calendar.ics）
python subscription_services/generate_subscription_calendar.py
```

4) 打开前端页面

直接在浏览器打开根目录下的 `index.html`。
页面会读取上述 YAML 并渲染表格，同时提供 ICS 链接输入框，便于复制到日历应用。

## 配置说明与最佳实践

* __日期格式__：统一使用 `YYYY-MM-DD`。对于 SSL 证书目标，允许为 `null`（未知或未采集），前端显示“未知”，日历生成脚本将跳过。
* __SSL 目标格式__：`domains_ssl_expiry` 的键可包含协议与端口（如 `https://asset.example.com:8801`）。
* __容错__：`generate_domain_calendar.py` 会自动跳过空值/非法日期，避免生成 ICS 时报错。
* __路径__：默认输出到各自模块目录下的 `.ics` 文件；如需变更，可调整脚本输出路径或前端 `index.html` 中的 ICS URL 拼装逻辑。

## 自动化运行（可选）

项目包含 GitHub Actions 工作流 `schedule_automation.yml`，可用于：

* __定时任务__：每天检查与更新
* __自动产物__：生成并提交最新 ICS 文件

## 依赖清单

详见 `requirements.txt`，主要包括：

* __pyyaml__：解析 YAML 配置
* __icalendar__：生成 ICS 文件
* __pytz__：时区处理
* __python-whois__：域名信息（可选）
* __pyOpenSSL__：证书信息（可选）
* __dnspython__：DNS 查询（可选）
* __certifi__：证书信任（可选）

## 常见问题

* __SSL 配置为 null 怎么办？__
  - 前端显示“未知”，ICS 生成时会被跳过，不会报错。
* __如何只导入某一类提醒？__
  - 分别使用两个 ICS 文件，按需导入。