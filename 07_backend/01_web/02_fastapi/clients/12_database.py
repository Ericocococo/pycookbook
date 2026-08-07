"""12_database.py 的 requests 客户端。先启动: python 12_database.py --serve"""

from _utils import get, post, put, delete

BASE = "http://127.0.0.1:8032"

post(f"{BASE}/user", json={"name": "张三", "age": 25})
post(f"{BASE}/user", json={"name": "李四", "age": 30})
get(f"{BASE}/user/1")
get(f"{BASE}/users")
put(f"{BASE}/user/1", json={"name": "张三改", "age": 26})
delete(f"{BASE}/user/2")
get(f"{BASE}/users")
