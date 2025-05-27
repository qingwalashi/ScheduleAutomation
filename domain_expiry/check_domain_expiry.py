#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import socket
import ssl
import datetime
import OpenSSL
import dns.resolver
from typing import Dict, List, Tuple
import logging
import certifi
import traceback
import whois
import requests
from urllib.parse import urlparse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_yaml(file_path):
    """加载YAML文件"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def save_yaml(data, file_path):
    """保存YAML文件"""
    with open(file_path, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, allow_unicode=True, sort_keys=False)

def check_domain_expiry(domain):
    """检查域名到期时间"""
    try:
        w = whois.whois(domain)
        if w.expiration_date:
            if isinstance(w.expiration_date, list):
                return w.expiration_date[0].strftime('%Y-%m-%d')
            return w.expiration_date.strftime('%Y-%m-%d')
    except Exception as e:
        print(f"检查域名 {domain} 到期时间时出错: {str(e)}")
    return None

def check_ssl_expiry(domain):
    """检查SSL证书到期时间"""
    try:
        # 尝试获取SSL证书
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                if cert and 'notAfter' in cert:
                    # 解析证书到期时间
                    expiry_date = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    return expiry_date.strftime('%Y-%m-%d')
    except Exception as e:
        print(f"检查域名 {domain} 的SSL证书到期时间时出错: {str(e)}")
    return None

def check_dns_records(domain):
    """检查DNS记录"""
    records = {}
    record_types = ['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'NS']
    
    for record_type in record_types:
        try:
            answers = dns.resolver.resolve(domain, record_type)
            records[record_type] = [str(rdata) for rdata in answers]
        except Exception as e:
            print(f"检查域名 {domain} 的 {record_type} 记录时出错: {str(e)}")
            records[record_type] = []
    
    return records

def check_website_status(domain):
    """检查网站状态"""
    try:
        # 尝试访问网站
        response = requests.get(f'https://{domain}', timeout=10, verify=False)
        return {
            'status_code': response.status_code,
            'is_accessible': 200 <= response.status_code < 400
        }
    except Exception as e:
        print(f"检查域名 {domain} 的网站状态时出错: {str(e)}")
        return {
            'status_code': None,
            'is_accessible': False
        }

def update_config_with_expiry_dates(config: Dict) -> Dict:
    """更新配置文件中的到期时间信息"""
    # 获取所有需要检查的域名
    domains_to_check = set()
    if 'domains_expiry' in config:
        domains_to_check.update(config['domains_expiry'].keys())
    if 'domains_ssl_expiry' in config:
        domains_to_check.update(config['domains_ssl_expiry'].keys())

    # 更新域名到期时间信息
    domains_expiry = {}
    for domain in domains_to_check:
        expiry_date = check_domain_expiry(domain)
        if expiry_date:
            domains_expiry[domain] = expiry_date
            logger.info(f"域名 {domain} 到期时间: {expiry_date}")
    config['domains_expiry'] = domains_expiry

    # 更新SSL证书到期时间信息
    domains_ssl_expiry = {}
    for domain in domains_to_check:
        expiry_date = check_ssl_expiry(domain)
        if expiry_date:
            domains_ssl_expiry[domain] = expiry_date
            logger.info(f"域名 {domain} 的SSL证书到期时间: {expiry_date}")
    config['domains_ssl_expiry'] = domains_ssl_expiry

    return config

def main():
    """主函数"""
    try:
        # 加载配置
        config = load_yaml('domain_expiry.yaml')
        
        # 更新到期时间信息
        updated_config = update_config_with_expiry_dates(config)
        
        # 保存更新后的配置
        save_yaml(updated_config, 'domain_expiry.yaml')
        
        logger.info("配置更新完成")
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        raise

if __name__ == "__main__":
    main() 