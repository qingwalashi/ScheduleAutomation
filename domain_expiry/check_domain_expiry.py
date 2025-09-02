#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import socket
import ssl
import datetime
import OpenSSL
import logging
import os
import traceback
from typing import Dict
from urllib.parse import urlparse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config() -> Dict:
    """加载配置文件"""
    try:
        # 获取脚本所在目录的绝对路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, 'domain_expiry.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"读取配置文件失败: {e}")
        raise

def save_config(config: Dict) -> None:
    """保存配置文件"""
    try:
        # 获取脚本所在目录的绝对路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, 'domain_expiry.yaml')
        with open(config_path, 'w', encoding='utf-8') as f:
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

def _parse_host_port(domain: str) -> tuple[str, int]:
    """从输入中解析主机与端口，支持如下格式：
    - host
    - host:port
    - https://host
    - https://host:port
    其他 scheme 一律默认用 443 端口进行 TLS 连接。
    """
    if not domain:
        return None, None
    d = domain.strip()
    # 先尝试当作 URL 解析
    parsed = urlparse(d)
    if parsed.scheme and parsed.netloc:
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme.lower() == 'https' else 443)
        return host, port
    # 非 URL，处理 host:port
    if ':' in d and d.count(':') == 1:
        host, port_str = d.split(':', 1)
        try:
            port = int(port_str)
        except ValueError:
            port = 443
        return host.strip(), port
    # 仅 host
    return d, 443

def check_ssl_expiry(domain: str) -> datetime.datetime:
    """检查SSL证书到期时间"""
    try:
        # 验证域名格式
        if not domain or not isinstance(domain, str):
            logger.error(f"无效的域名格式: {domain}")
            return None
        
        # 解析主机与端口
        host, port = _parse_host_port(domain)
        if not host or not port:
            logger.error(f"无法从输入解析主机和端口: {domain}")
            return None
        
        # 尝试解析主机名
        try:
            socket.gethostbyname(host)
        except socket.gaierror:
            logger.error(f"无法解析域名: {domain}")
            return None
            
        # 创建SSL上下文
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        # 创建连接
        conn = context.wrap_socket(
            socket.socket(socket.AF_INET),
            server_hostname=host,
        )
        conn.settimeout(10)
        
        # 连接服务器
        try:
            conn.connect((host, port))
        except (socket.gaierror, socket.timeout, ConnectionRefusedError) as e:
            logger.error(f"连接域名 {domain} 失败: {str(e)}")
            return None
        
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
    # 更新域名到期时间信息（仅在查询成功时覆盖原值，失败则保留原值，不删除任何域名行）
    original_domains_expiry = config.get('domains_expiry', {}) or {}
    updated_domains_expiry = dict(original_domains_expiry)
    for domain in original_domains_expiry.keys():
        expiry_date = check_domain_expiry(domain)
        if expiry_date:
            updated_domains_expiry[domain] = expiry_date.strftime('%Y-%m-%d')
            logger.info(f"域名 {domain} 到期时间: {expiry_date.strftime('%Y-%m-%d')}")
        else:
            logger.info(f"域名 {domain} 到期时间查询失败，保留原值: {original_domains_expiry.get(domain)}")
    config['domains_expiry'] = updated_domains_expiry

    # 更新SSL证书到期时间信息（同样策略：只覆盖成功的，不删除条目）
    original_domains_ssl_expiry = config.get('domains_ssl_expiry', {}) or {}
    updated_domains_ssl_expiry = dict(original_domains_ssl_expiry)
    for domain in original_domains_ssl_expiry.keys():
        expiry_date = check_ssl_expiry(domain)
        if expiry_date:
            updated_domains_ssl_expiry[domain] = expiry_date.strftime('%Y-%m-%d')
            logger.info(f"域名 {domain} 的SSL证书到期时间: {expiry_date.strftime('%Y-%m-%d')}")
        else:
            logger.info(f"域名 {domain} 的SSL证书到期时间查询失败，保留原值: {original_domains_ssl_expiry.get(domain)}")
    config['domains_ssl_expiry'] = updated_domains_ssl_expiry

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