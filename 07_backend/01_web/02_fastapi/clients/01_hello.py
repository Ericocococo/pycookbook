"""01_hello.py 的 requests 客户端。先启动: python 01_hello.py --serve"""

from _utils import get

BASE = "http://127.0.0.1:8021"

get(f"{BASE}/")       # 纯文本
get(f"{BASE}/json")   # JSON
