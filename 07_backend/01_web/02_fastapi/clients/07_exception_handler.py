"""07_exception_handler.py 的 requests 客户端。先启动: python 07_exception_handler.py --serve"""

from _utils import post

BASE = "http://127.0.0.1:8027"

post(f"{BASE}/order", json={"item": "手机", "quantity": 2})
post(f"{BASE}/order", json={"item": "手机", "quantity": 99})
post(f"{BASE}/order", json={"item": "手机", "quantity": -1})
