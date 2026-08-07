"""04_pydantic_depends.py 的 requests 客户端。先启动: python 04_pydantic_depends.py --serve"""

from _utils import get, post

BASE = "http://127.0.0.1:8024"

post(f"{BASE}/user", json={"name": "赵六", "age": 20})
post(f"{BASE}/user", json={"name": "错误", "age": -5})
get(f"{BASE}/secure", params={"token": "secret"})
get(f"{BASE}/secure", params={"token": "wrong"})
