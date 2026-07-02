"""
04_pydantic_depends.py —— FastAPI 特色:Pydantic 数据校验 + 依赖注入 + 自动文档
================================================================================
所属: 三方库 FastAPI + Pydantic 2 | Python 3.12

运行:
  python 04_pydantic_depends.py         # 自测:真实 curl 打一遍(含一条 422 校验失败)
  python 04_pydantic_depends.py --serve   # 起服务后:
    curl -X POST http://127.0.0.1:8024/user \
         -H 'Content-Type: application/json' -d '{"name":"赵六","age":20}'
    curl 'http://127.0.0.1:8024/secure?token=secret'   # 依赖注入鉴权
    浏览器打开 http://127.0.0.1:8024/docs                # Pydantic 模型自动生成文档

要点(这几样是 FastAPI 相比其他框架的核心优势):
  ① BaseModel —— 用类型注解声明请求体结构,自动校验;不合法自动返回 422
  ② Field —— 给字段加约束(如 age 必须 > 0)
  ③ Depends —— 依赖注入:把「取当前用户 / 校验 token / 连数据库」抽成可复用依赖
  ④ /docs —— 基于以上信息自动生成交互式 API 文档,零额外代码
================================================================================
"""

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

PORT = 8024
app = FastAPI()


class User(BaseModel):                 # ① Pydantic 模型 = 请求体结构 + 校验规则
    name: str
    age: int = Field(gt=0, le=150)     # ② 约束:0 < age <= 150,越界自动 422


@app.post("/user", status_code=201)
async def create_user(user: User):
    """参数是 Pydantic 模型 → 自动解析并校验请求体,失败自动 422。"""
    return {"created": user.model_dump()}


def verify_token(token: str = Query(default="")):
    """③ 一个依赖:校验查询参数里的 token,失败抛 401。"""
    if token != "secret":
        raise HTTPException(status_code=401, detail="token 无效")
    return {"user": "authorized-user"}


@app.get("/secure")
async def secure(identity: dict = Depends(verify_token)):
    """④ Depends(verify_token):进函数前先跑依赖,拿到返回值注入 identity。"""
    return {"msg": "已通过鉴权", "identity": identity}


CURL_CASES = [
    {"desc": "合法请求体 → 201 创建", "method": "POST", "path": "/user",
     "json": {"name": "赵六", "age": 20}},
    {"desc": "age=-5 违反约束 → Pydantic 自动 422", "method": "POST", "path": "/user",
     "json": {"name": "错误", "age": -5}},
    {"desc": "依赖注入:token 正确 → 放行", "path": "/secure?token=secret"},
    {"desc": "依赖注入:token 错误 → 401", "path": "/secure?token=wrong"},
]


if __name__ == "__main__":
    import argparse
    _ap = argparse.ArgumentParser()
    _ap.add_argument("--serve", action="store_true",
                     help="阻塞启动服务，供手动 curl / IDE 断点调试")
    if _ap.parse_args().serve:
        uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
    else:
        from _curl_selftest import run_selftest
        run_selftest(__file__, "127.0.0.1", PORT, CURL_CASES)
