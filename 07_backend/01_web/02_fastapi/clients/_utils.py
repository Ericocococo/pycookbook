"""
clients 公共工具：统一的请求函数。

用法:
    from _utils import get, post, put, delete

    get("http://127.0.0.1:8021/")
    post("http://127.0.0.1:8021/user", json={"name": "张三"})
    get("http://127.0.0.1:8021/me", token="xxx")
    post("http://127.0.0.1:8021/login", data={"username": "admin"})
    post("http://127.0.0.1:8021/upload", files={"file": ("a.txt", b"hi")})
    get("http://127.0.0.1:8021/headers", show_headers=True)
"""

import random

import requests


def _ua() -> str:
    n1 = random.randint(55, 62)
    n3 = random.randint(0, 3200)
    n4 = random.randint(0, 140)
    os_list = ["(Windows NT 10.0; WOW64)", "(X11; Linux x86_64)", "(Macintosh; Intel Mac OS X 10_12_6)"]
    return f"Mozilla/5.0 {random.choice(os_list)} AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{n1}.0.{n3}.{n4} Safari/537.36"


def _do(method, url, *, json=None, data=None, params=None, files=None,
        token=None, cookies=None, headers=None, show_headers=False):
    """发请求 + 打印结果。"""
    h = {"User-Agent": _ua()}
    if token:
        h["Authorization"] = f"Bearer {token}"
    if headers:
        h.update(headers)

    print(f"\n{'─' * 50}")
    print(f"  {method} {url}")

    try:
        r = requests.request(method, url, json=json, data=data, params=params,
                             files=files, headers=h, cookies=cookies, timeout=15)
        try:
            print(f"  [{r.status_code}] {r.json()}")
        except ValueError:
            print(f"  [{r.status_code}] {r.text[:200]}")

        if show_headers:
            for k, v in r.headers.items():
                if k.lower().startswith("x-") or k.lower() in ("location", "set-cookie"):
                    print(f"  {k}: {v}")
        return r
    except requests.ConnectionError:
        print("  [错误] 连接失败，请先启动服务")
        return None


def get(url, **kw):
    return _do("GET", url, **kw)


def post(url, **kw):
    return _do("POST", url, **kw)


def put(url, **kw):
    return _do("PUT", url, **kw)


def delete(url, **kw):
    return _do("DELETE", url, **kw)
