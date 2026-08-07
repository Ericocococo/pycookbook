"""10_file.py 的 requests 客户端。先启动: python 10_file.py --serve"""

from _utils import get, post

BASE = "http://127.0.0.1:8030"

post(f"{BASE}/upload", files={"file": ("demo.txt", b"hello fastapi", "text/plain")})
get(f"{BASE}/")
get(f"{BASE}/download/demo.txt")
