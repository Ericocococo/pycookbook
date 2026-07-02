"""
01_hello.py —— Tornado 最小应用
================================================================================
所属: 三方库 Tornado 6.x | Python 3.12 | 安装: pip install tornado

两种运行方式:
  ① 自测(推荐):python 01_hello.py
  ② 手动:python 01_hello.py --serve,再另开终端:
        curl http://127.0.0.1:9031/            # 纯文本
        curl http://127.0.0.1:9031/json        # JSON

Tornado 是异步框架,用**类**组织请求处理:
  - 每个 URL 对应一个 RequestHandler 子类,在类里定义 get/post/... 方法
  - Application 把 (正则路径, Handler) 映射成路由表
  - 现基于 asyncio 事件循环运行
================================================================================
"""
import asyncio
import json

import tornado.web

PORT = 9031


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        """纯文本:self.write 写响应体。"""
        self.write("Hello Tornado")


class JsonHandler(tornado.web.RequestHandler):
    def get(self):
        """JSON:手动 dumps(ensure_ascii=False)让中文直接输出并设好类型。"""
        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.write(json.dumps({"framework": "tornado", "msg": "你好"},
                              ensure_ascii=False))


def make_app():
    """Application = 路由表:每项 (URL 正则, Handler 类)。"""
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/json", JsonHandler),
    ])


async def main():
    """异步启动:listen 绑定端口后,用 Event().wait() 挂起保持运行。"""
    make_app().listen(PORT, address="127.0.0.1")
    await asyncio.Event().wait()


CURL_CASES = [
    {"desc": "根路由,返回纯文本", "path": "/"},
    {"desc": "返回 JSON", "path": "/json"},
]


if __name__ == "__main__":
    import argparse
    _ap = argparse.ArgumentParser()
    _ap.add_argument("--serve", action="store_true",
                     help="阻塞启动服务，供手动 curl / IDE 断点调试")
    if _ap.parse_args().serve:
        asyncio.run(main())
    else:
        from _curl_selftest import run_selftest
        run_selftest(__file__, "127.0.0.1", PORT, CURL_CASES)
