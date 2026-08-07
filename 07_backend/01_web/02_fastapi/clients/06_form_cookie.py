"""06_form_cookie.py 的 requests 客户端。先启动: python 06_form_cookie.py --serve"""

from _utils import get, post

BASE = "http://127.0.0.1:8026"

post(f"{BASE}/login", data={"username": "admin", "password": "123"}, show_headers=True)
get(f"{BASE}/me", cookies={"session_id": "abc123"})
get(f"{BASE}/me")  # 无 Cookie → 401
