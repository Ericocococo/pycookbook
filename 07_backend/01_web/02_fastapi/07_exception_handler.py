"""
07_exception_handler.py —— 自定义异常处理：统一错误格式
================================================================================
所属: 三方库 FastAPI | Python 3.12

运行:
  python 07_exception_handler.py         # 自测
  python 07_exception_handler.py --serve  # 起服务

要点:
  ① 自定义异常类 —— 业务错误用自己的异常，和 HTTP 错误分开
  ② @app.exception_handler —— 注册全局异常处理器，统一错误响应格式
  ③ 覆盖 422 默认格式 —— Pydantic 校验失败也走统一格式
================================================================================
"""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

PORT = 8027
app = FastAPI()


# ── ① 自定义业务异常 ──
class BizError(Exception):
    """业务逻辑错误（如"余额不足""库存不够"）。"""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message


# ── ② 注册全局异常处理器 ──
@app.exception_handler(BizError)
async def biz_error_handler(request: Request, exc: BizError):
    """捕获所有 BizError，返回统一格式 {"error": code, "message": ...}。"""
    return JSONResponse(
        status_code=400,
        content={"error": exc.code, "message": exc.message},
    )


# ── ③ 覆盖 422 校验错误的默认格式 ──
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Pydantic 校验失败也走统一格式，而非 FastAPI 默认的 422 格式。"""
    return JSONResponse(
        status_code=422,
        content={"error": "VALIDATION_ERROR", "message": str(exc.errors())},
    )


class OrderCreate(BaseModel):
    item: str
    quantity: int = Field(gt=0)


@app.post("/order")
async def create_order(order: OrderCreate):
    """模拟下单：库存不够抛 BizError。"""
    if order.quantity > 10:
        raise BizError("STOCK_INSUFFICIENT", f"库存不足，最多 10 件，你要 {order.quantity} 件")
    return {"msg": "下单成功", "order": order.model_dump()}


CURL_CASES = [
    {"desc": "正常下单", "method": "POST", "path": "/order",
     "json": {"item": "手机", "quantity": 2}},
    {"desc": "库存不足 → BizError 统一格式", "method": "POST", "path": "/order",
     "json": {"item": "手机", "quantity": 99}},
    {"desc": "quantity=-1 → 422 统一格式", "method": "POST", "path": "/order",
     "json": {"item": "手机", "quantity": -1}},
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
