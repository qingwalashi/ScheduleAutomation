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

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config() -> Dict:
    """加载配置文件"""
    try:
        with open('domain_expiry/domain_expiry.yaml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"读取配置文件失败: {e}")
        raise

def save_config(config: Dict) -> None:
    """保存配置文件"""
    try:
        with open('domain_expiry/domain_expiry.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    except Exception as e:
        logger.error(f"保存配置文件失败: {e}")
        raise

def check_domain_expiry(domain: str) -> datetime.datetime:
    """检查域名到期时间"""
    try:
        # 使用 whois 查询域名信息
        import whois
        domain_info = whois.whois(domain)
        if domain_info.expiration_date:
            if isinstance(domain_info.expiration_date, list):
                return domain_info.expiration_date[0]
            return domain_info.expiration_date
        return None
    except Exception as e:
        logger.error(f"检查域名 {domain} 到期时间失败: {e}")
        return None

def check_ssl_expiry(domain: str) -> datetime.datetime:
    """检查SSL证书到期时间"""
    try:
        # 创建SSL上下文
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        # 创建连接
        conn = context.wrap_socket(
            socket.socket(socket.AF_INET),
            server_hostname=domain,
        )
        conn.settimeout(10)
        
        # 连接服务器
        conn.connect((domain, 443))
        
        # 获取证书
        cert = conn.getpeercert(binary_form=True)
        if cert:
            # 使用OpenSSL解析证书
            x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, cert)
            # 获取到期时间
            expiry_date = datetime.datetime.strptime(
                x509.get_notAfter().decode('ascii'),
                '%Y%m%d%H%M%SZ'
            )
            return expiry_date
            
        return None
    except Exception as e:
        logger.error(f"检查域名 {domain} 的SSL证书到期时间失败: {str(e)}")
        logger.error(f"详细错误信息: {traceback.format_exc()}")
        return None
    finally:
        try:
            conn.close()
        except:
            pass

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
            domains_expiry[domain] = expiry_date.strftime('%Y-%m-%d')
            logger.info(f"域名 {domain} 到期时间: {expiry_date.strftime('%Y-%m-%d')}")
    config['domains_expiry'] = domains_expiry

    # 更新SSL证书到期时间信息
    domains_ssl_expiry = {}
    for domain in domains_to_check:
        expiry_date = check_ssl_expiry(domain)
        if expiry_date:
            domains_ssl_expiry[domain] = expiry_date.strftime('%Y-%m-%d')
            logger.info(f"域名 {domain} 的SSL证书到期时间: {expiry_date.strftime('%Y-%m-%d')}")
    config['domains_ssl_expiry'] = domains_ssl_expiry

    return config

def main():
    """主函数"""
    try:
        # 加载配置
        config = load_config()
        
        # 更新到期时间信息
        updated_config = update_config_with_expiry_dates(config)
        
        # 保存更新后的配置
        save_config(updated_config)
        
        logger.info("配置更新完成")
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        raise

if __name__ == "__main__":
    main() 