"""13_background_task.py 的 requests 客户端。先启动: python 13_background_task.py --serve"""

import time

from _utils import get, post

BASE = "http://127.0.0.1:8033"

post(f"{BASE}/register?name=张三")
post(f"{BASE}/register?name=李四")
print("\n  等 2 秒让后台任务完成...")
time.sleep(2)
get(f"{BASE}/tasks")
