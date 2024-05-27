import re
from ..config import Config

__all__ = ("hide_ip",)

def hide_ip(url: str, config: Config):
    ipv4_re = "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    ipv6_re = "([a-f0-9:]+:+)+[a-f0-9]+"

    if config.hide_ip:
        url = re.sub(ipv4_re, "{the-cat-snatched-your-ip-address}", url)
        url = re.sub(ipv6_re, "{the-cat-snatched-your-ip-address}", url)

    return url