"""
13_background_task.py —— BackgroundTasks：后台异步任务
================================================================================
所属: 三方库 FastAPI | Python 3.12

运行:
  python 13_background_task.py         # 自测
  python 13_background_task.py --serve  # 起服务

要点:
  ① BackgroundTasks —— 在返回响应后继续执行耗时操作（发邮件、写日志等）
  ② 响应先返回，任务后台跑 —— 用户不用等
  ③ 和 Depends 组合 —— 依赖里也能加后台任务
================================================================================
"""

import time

import uvicorn
from fastapi import BackgroundTasks, FastAPI

PORT = 8033
app = FastAPI()

TASK_LOG: list[str] = []


def send_email(to: str, subject: str):
    """模拟发邮件（耗时操作）。"""
    time.sleep(1)
    msg = f"邮件已发送: to={to}, subject={subject}"
    TASK_LOG.append(msg)
    print(f"  [后台] {msg}")


@app.post("/register")
async def register(name: str, bg: BackgroundTasks):
    """① 注册后发欢迎邮件（后台执行，用户不用等 1 秒）。"""
    bg.add_task(send_email, to=f"{name}@example.com", subject="欢迎注册")
    return {"msg": f"{name} 注册成功（欢迎邮件后台发送中）"}


@app.get("/tasks")
async def list_tasks():
    """查看已完成的后台任务。"""
    return {"completed_tasks": TASK_LOG}


CURL_CASES = [
    {"desc": "注册 → 响应立刻返回，邮件后台发", "method": "POST", "path": "/register?name=张三"},
    {"desc": "注册第二个", "method": "POST", "path": "/register?name=李四"},
    {"desc": "查看后台任务完成情况（可能还在跑）", "path": "/tasks"},
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
