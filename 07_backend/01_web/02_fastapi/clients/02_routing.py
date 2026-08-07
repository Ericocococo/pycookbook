"""02_routing.py 的 requests 客户端。先启动: python 02_routing.py --serve"""

from _utils import get, post, put, delete

BASE = "http://127.0.0.1:8022"

get(f"{BASE}/user/1")                        # 路径参数
get(f"{BASE}/user/99")                       # 404
get(f"{BASE}/users", params={"limit": 1})    # 查询参数
post(f"{BASE}/user")                         # 创建
put(f"{BASE}/user/1")                        # 更新
delete(f"{BASE}/user/2")                     # 删除
