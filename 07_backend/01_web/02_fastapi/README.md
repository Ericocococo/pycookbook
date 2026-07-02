# FastAPI —— 现代异步 Web 框架(三方库,基于 Starlette + Pydantic)

| 文件 | 内容 |
|------|------|
| `01_hello.py` | 最小应用:@app.get + async 函数,返回 dict 自动转 JSON |
| `02_routing.py` | 类型注解决定路径/查询参数;GET/POST/PUT/DELETE;类型错自动 422 |
| `03_request_response.py` | dict 参数收 JSON body、Header 读请求头、自定义状态码/响应头 |
| `04_pydantic_depends.py` | 特色:Pydantic 校验(422)+ Depends 依赖注入 + /docs 自动文档 |
| `_curl_selftest.py` | 【工具,非配方】起服务 + 真实 curl 自测助手 |

## 运行方式

```bash
python 01_hello.py            —— 自测:起 uvicorn 服务 + 真实 curl 打一遍
python 01_hello.py --serve      —— 只起服务;再访问 /docs 看自动生成的交互文档
```

## 适用

- REST API、微服务、后端接口(当下最推荐)
- 需要请求数据校验(Pydantic)且不想手写
- 需要自动生成 API 文档(/docs、/redoc)
- I/O 密集、高并发(async 原生)

## 不适用

- 传统服务端渲染页面为主 → Flask 更顺手
- WebSocket / 长连接为主 → Tornado 更成熟
- 团队完全不用类型注解 → 优势发挥不出来

## 核心速查

```python
from fastapi import FastAPI, Depends
from pydantic import BaseModel
app = FastAPI()
class User(BaseModel):            # 请求体结构 + 自动校验
    name: str; age: int
@app.get("/user/{uid}")          # {uid}+注解=路径参数; 带默认值=查询参数
async def get(uid: int, q: str = ""):
    return {"uid": uid, "q": q}  # 返回 dict 自动 JSON
@app.post("/user")
async def create(u: User): ...   # 参数是模型 → 自动解析+校验请求体
# 启动: uvicorn 文件名:app --reload ; 文档: http://127.0.0.1:8000/docs

```

> 四框架横向对比见 [01_flask/README.md](../01_flask/README.md)
