"""Configuration loader for BoscoTsang.

Loads `BoscoTsang.toml` from application base directory (APP_BASE_DIR) or repository root.
Provides helper to access proxy settings and applies environment variables for global/none modes.
"""
import ipaddress
import os
import socket
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    # Python 3.11+
    import tomllib as _toml
except Exception:
    try:
        import tomli as _toml  # type: ignore
    except Exception:
        _toml = None


def _read_toml(path: Path) -> Dict[str, Any]:
    if not path.exists() or not _toml:
        return {}
    with open(path, 'rb') as f:
        return _toml.load(f)


def load_config(base_dir: Path) -> Dict[str, Any]:
    """Load configuration from BoscoTsang.toml under base_dir or project root."""
    cfg_path = Path(os.getenv('APP_BASE_DIR', base_dir)) / 'BoscoTsang.toml'
    if not cfg_path.exists():
        cfg_path = Path.cwd() / 'BoscoTsang.toml'
    return _read_toml(cfg_path) if cfg_path.exists() else {}


def _parse_cidrs(values: Optional[List[str]]) -> List[ipaddress._BaseNetwork]:
    networks = []
    if not values:
        return networks
    for value in values:
        try:
            networks.append(ipaddress.ip_network(value, strict=False))
        except Exception:
            continue
    return networks


def is_local_address(hostname: str, bypass_cidrs: Optional[List[str]] = None) -> bool:
    """判断目标是否为本地/国内网段或可直接直连的地址。"""
    if not hostname:
        return False

    # IP 地址直接判断
    try:
        ip = ipaddress.ip_address(hostname)
        if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local:
            return True
        for network in _parse_cidrs(bypass_cidrs):
            if ip in network:
                return True
        return False
    except ValueError:
        pass

    # 域名规则判断，仅做参考。
    hostname = hostname.lower().strip()
    domestic_suffixes = (
        '.cn', '.com.cn', '.net.cn', '.gov.cn', '.edu.cn',
        '.cc', '.top', '.vip', '.wang'
    )
    if hostname.endswith(domestic_suffixes):
        return True

    # 常见国内站点关键词
    domestic_domains = ('baidu.', 'qq.', 'taobao.', 'jd.', 'sina.', 'weibo.', 'bilibili.', 'douyin.', 'xiaohongshu.', 'kuaishou.', 'qqmusic.')
    if any(hostname.startswith(d) or d in hostname for d in domestic_domains):
        return True

    # 解析 DNS，若解析到本地地址也视为直连
    try:
        infos = socket.getaddrinfo(hostname, None)
        for info in infos:
            addr = info[4][0]
            try:
                ip = ipaddress.ip_address(addr)
                if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local:
                    return True
                for network in _parse_cidrs(bypass_cidrs):
                    if ip in network:
                        return True
            except Exception:
                continue
    except Exception:
        pass

    return False


def get_proxy_config(cfg: Dict[str, Any]) -> Dict[str, Any]:
    proxy_cfg = cfg.get('proxy', {}) if cfg else {}
    return {
        'enabled': bool(proxy_cfg.get('enabled', True)),
        'mode': str(proxy_cfg.get('mode', 'auto')).lower(),
        'http': proxy_cfg.get('http', ''),
        'https': proxy_cfg.get('https', ''),
        'bypass_cidrs': proxy_cfg.get('bypass_cidrs', []) or []
    }


def apply_proxy_from_config(cfg: Dict[str, Any]):
    """Apply proxy environment variables for global/none modes.

    - If mode is 'global' and proxy URLs exist, set `HTTP_PROXY`/`HTTPS_PROXY` env vars.
    - If mode is 'none', remove those env vars.
    - If mode is 'auto', do not change env vars globally; leave to per-request logic.
    """
    proxy = get_proxy_config(cfg)
    if not proxy['enabled']:
        os.environ.pop('HTTP_PROXY', None)
        os.environ.pop('HTTPS_PROXY', None)
        return

    if proxy['mode'] == 'global':
        if proxy['http']:
            os.environ['HTTP_PROXY'] = str(proxy['http'])
        if proxy['https']:
            os.environ['HTTPS_PROXY'] = str(proxy['https'])
    elif proxy['mode'] == 'none':
        os.environ.pop('HTTP_PROXY', None)
        os.environ.pop('HTTPS_PROXY', None)


__all__ = ['load_config', 'apply_proxy_from_config']
