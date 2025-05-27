#!/usr/bin/env python3
import yaml
from datetime import datetime, timedelta
from icalendar import Calendar, Event
import pytz
import os

def read_yaml_file(file_path):
    """读取YAML文件内容"""
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建配置文件的完整路径
    config_path = os.path.join(script_dir, file_path)
    with open(config_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def create_calendar_events(data):
    """创建日历事件"""
    cal = Calendar()
    cal.add('prodid', '-//Domain Expiry Calendar//CN')
    cal.add('version', '2.0')
    cal.add('name', '域名到期提醒')
    cal.add('description', '域名和SSL证书到期提醒')

    # 设置时区
    tz = pytz.timezone('Asia/Shanghai')

    # 处理域名到期
    for domain, expiry_date in data.get('domains_expiry', {}).items():
        # 创建到期事件
        event = Event()
        event.add('summary', f'域名到期提醒: {domain}')
        event.add('description', f'域名 {domain} 将在 {expiry_date} 到期')
        event.add('dtstart', datetime.strptime(expiry_date, '%Y-%m-%d').date())
        event.add('dtend', datetime.strptime(expiry_date, '%Y-%m-%d').date() + timedelta(days=1))
        event.add('dtstamp', datetime.now(tz))
        cal.add_component(event)

        # 创建提前7天提醒事件
        reminder_date = datetime.strptime(expiry_date, '%Y-%m-%d').date() - timedelta(days=7)
        reminder = Event()
        reminder.add('summary', f'域名即将到期提醒: {domain}')
        reminder.add('description', f'域名 {domain} 将在7天后（{expiry_date}）到期')
        reminder.add('dtstart', reminder_date)
        reminder.add('dtend', reminder_date + timedelta(days=1))
        reminder.add('dtstamp', datetime.now(tz))
        cal.add_component(reminder)

    # 处理SSL证书到期
    for domain, expiry_date in data.get('domains_ssl_expiry', {}).items():
        # 创建到期事件
        event = Event()
        event.add('summary', f'SSL证书到期提醒: {domain}')
        event.add('description', f'域名 {domain} 的SSL证书将在 {expiry_date} 到期')
        event.add('dtstart', datetime.strptime(expiry_date, '%Y-%m-%d').date())
        event.add('dtend', datetime.strptime(expiry_date, '%Y-%m-%d').date() + timedelta(days=1))
        event.add('dtstamp', datetime.now(tz))
        cal.add_component(event)

        # 创建提前7天提醒事件
        reminder_date = datetime.strptime(expiry_date, '%Y-%m-%d').date() - timedelta(days=7)
        reminder = Event()
        reminder.add('summary', f'SSL证书即将到期提醒: {domain}')
        reminder.add('description', f'域名 {domain} 的SSL证书将在7天后（{expiry_date}）到期')
        reminder.add('dtstart', reminder_date)
        reminder.add('dtend', reminder_date + timedelta(days=1))
        reminder.add('dtstamp', datetime.now(tz))
        cal.add_component(reminder)

    return cal

def save_ics_file(cal, output_path):
    """保存ICS文件"""
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建输出文件的完整路径
    output_path = os.path.join(script_dir, output_path)
    with open(output_path, 'wb') as f:
        f.write(cal.to_ical())

def main():
    try:
        # 读取YAML文件
        yaml_data = read_yaml_file('domain_expiry.yaml')
        
        # 创建日历事件
        calendar = create_calendar_events(yaml_data)
        
        # 保存ICS文件
        save_ics_file(calendar, 'domain_expiry_calendar.ics')
        print("日历文件已生成: domain_expiry_calendar.ics")
    except Exception as e:
        print(f"程序执行失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main() 