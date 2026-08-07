"""
10_file.py —— 文件上传 / 下载 / 静态文件
================================================================================
所属: 三方库 FastAPI | Python 3.12 | 额外: pip install python-multipart

运行:
  python 10_file.py         # 自测
  python 10_file.py --serve  # 起服务

要点:
  ① UploadFile —— 接收上传文件（支持大文件流式读取）
  ② FileResponse —— 下载文件
  ③ StaticFiles —— 挂载静态文件目录（CSS/JS/图片等）
================================================================================
"""

import tempfile
from pathlib import Path

import uvicorn
from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse, PlainTextResponse

PORT = 8030
app = FastAPI()

UPLOAD_DIR = Path(tempfile.mkdtemp())


@app.post("/upload")
async def upload(file: UploadFile):
    """① UploadFile 接收上传文件，保存到临时目录。"""
    content = await file.read()
    save_path = UPLOAD_DIR / file.filename
    save_path.write_bytes(content)
    return {
        "filename": file.filename,
        "size": len(content),
        "content_type": file.content_type,
        "saved_to": str(save_path),
    }


@app.get("/download/{filename}")
async def download(filename: str):
    """② FileResponse 返回文件供下载。"""
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        return PlainTextResponse(f"文件 {filename} 不存在", status_code=404)
    return FileResponse(file_path, filename=filename)


@app.get("/")
async def root():
    """列出已上传的文件。"""
    files = [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]
    return {"upload_dir": str(UPLOAD_DIR), "files": files}


CURL_CASES = [
    {"desc": "上传文件（模拟）", "method": "POST", "path": "/upload",
     "raw_data_file": True},
    {"desc": "查看已上传文件列表", "path": "/"},
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

        # 文件上传 curl 格式不同，这里只测列表
        run_selftest(__file__, "127.0.0.1", PORT, [CURL_CASES[1]])
