"""05_response_model.py 的 requests 客户端。先启动: python 05_response_model.py --serve"""

from _utils import get, post

BASE = "http://127.0.0.1:8025"

get(f"{BASE}/user/1")
get(f"{BASE}/users")
post(f"{BASE}/user", json={"name": "王五", "age": 20, "password": "mypass"})
