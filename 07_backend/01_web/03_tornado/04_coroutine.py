"""
04_coroutine.py —— Tornado 特色:异步协程 handler(await 异步 IO)
================================================================================
所属: 三方库 Tornado 6.x | Python 3.12

运行:
  python 04_coroutine.py         # 自测:真实 curl 打一遍(含并发验证)
  python 04_coroutine.py serve   # 起服务,手动 curl:
    curl 'http://127.0.0.1:9034/slow?ms=300'    # 单个慢请求(await 期间不阻塞别人)
    curl http://127.0.0.1:9034/gather           # 一个请求里并发发起多个异步任务

要点(Tornado 天生异步,擅长长连接/高并发 IO):
  ① async def get(self) —— 处理方法本身是协程,可以 await
  ② await asyncio.sleep —— 模拟异步 IO(查库/调外部接口);期间事件循环去服务别的请求
  ③ asyncio.gather —— 在一个请求内并发跑多个异步任务,总耗时≈最慢的那个
  说明:自测里会「同时」发多个 /slow,观察总耗时远小于串行之和 → 证明是并发处理。
================================================================================
"""
import asyncio
import json
import sys
import time

import tornado.web

PORT = 9034


def write_json(handler, obj, status=200):
    handler.set_status(status)
    handler.set_header("Content-Type", "application/json; charset=utf-8")
    handler.write(json.dumps(obj, ensure_ascii=False))


class SlowHandler(tornado.web.RequestHandler):
    async def get(self):                       # ① 处理方法是协程
        """② await 模拟异步 IO:sleep 期间不占线程,循环可服务其他请求。"""
        ms = int(self.get_query_argument("ms", default="200"))
        await asyncio.sleep(ms / 1000)
        write_json(self, {"slept_ms": ms})


async def fake_io(name, ms):
    """模拟一次异步 IO,返回耗时。"""
    await asyncio.sleep(ms / 1000)
    return {"task": name, "ms": ms}


class GatherHandler(tornado.web.RequestHandler):
    async def get(self):
        """③ 一个请求里用 gather 并发跑 3 个任务,总耗时≈最慢的 300ms 而非累加。"""
        start = time.monotonic()
        results = await asyncio.gather(
            fake_io("a", 100), fake_io("b", 200), fake_io("c", 300),
        )
        elapsed = round((time.monotonic() - start) * 1000)
        write_json(self, {"elapsed_ms": elapsed, "results": results})


def make_app():
    return tornado.web.Application([
        (r"/slow", SlowHandler),
        (r"/gather", GatherHandler),
    ])


async def main():
    make_app().listen(PORT, address="127.0.0.1")
    await asyncio.Event().wait()


CURL_CASES = [
    {"desc": "单个异步慢请求(sleep 300ms)", "path": "/slow?ms=300"},
    {"desc": "一个请求内并发 3 个任务(总耗时≈最慢 300ms)", "path": "/gather"},
]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        asyncio.run(main())
    else:
        from _curl_selftest import run_selftest
        run_selftest(__file__, "127.0.0.1", PORT, CURL_CASES)
