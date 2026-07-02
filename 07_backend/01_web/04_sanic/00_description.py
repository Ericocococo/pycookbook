"""
00_description.py
说明
================================================================================
本目录:Sanic —— 高性能异步 Web 框架(三方库)

【文件列表】
  01_hello.py                   —— 最小应用:@app.get + async handler,自带服务器 app.run
  02_routing.py                 —— 路径参数 <uid:int>、查询参数、GET/POST/PUT/DELETE
  03_request_response.py        —— request.json 收 body、读请求头、自定义状态码/响应头
  04_middleware_blueprint.py    —— 特色:中间件(on_request/on_response)+ 蓝图(Blueprint)
  _curl_selftest.py             —— 【工具,非配方】起服务 + 真实 curl 自测助手

【怎么运行】(已装在 conda 环境 quant312)
  python 01_hello.py            —— 自测:起服务 + 真实 curl 打一遍
  python 01_hello.py serve      —— 只起服务(演示用单进程),自己 curl
  说明:生产可 app.run(workers=N) 多进程;示例为方便自测用了 single_process=True。

【适用场景】
  ✔ 追求高吞吐的异步 API,又想要 Flask 式简洁装饰器写法
  ✔ 自带高性能服务器 + 原生多 worker,不想额外配 uvicorn/gunicorn
  ✔ I/O 密集、高并发

【不适用】
  ✘ 需要开箱即用的数据校验 + 自动文档 → FastAPI 更强
  ✘ WebSocket / 长连接为绝对核心 → Tornado 更成熟
  ✘ 传统同步 Web / 大量现成同步扩展 → Flask 生态更全

【核心速查】
  from sanic import Sanic, Blueprint
  from sanic.response import json as sjson, text
  app = Sanic("MyApp")                 # 必须给唯一名字
  @app.get("/user/<uid:int>")          # 路径参数带类型
  async def h(request, uid):           # 首参固定 request,且 async
      request.args.get("q")            # 查询参数
      request.json                     # 请求体 JSON
      return sjson({"id": uid}, status=201)
  app.run(host="127.0.0.1", port=8000, workers=2)   # 自带服务器,可多 worker

  四框架横向对比见 ../01_flask/00_description.py
================================================================================
"""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

print(__doc__)
