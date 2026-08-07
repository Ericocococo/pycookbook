"""14_auth.py 的 requests 客户端。先启动: python 14_auth.py --serve"""

from _utils import get, post

BASE = "http://127.0.0.1:8034"

post(f"{BASE}/register", json={"username": "admin", "password": "123"})
r = post(f"{BASE}/login", json={"username": "admin", "password": "123"})
token = r.json()["access_token"] if r else None

get(f"{BASE}/me")                # 无 token → 401
get(f"{BASE}/me", token=token)   # 带 token → 成功
