# FastAPI —— 现代异步 Web 框架(三方库,基于 Starlette + Pydantic)

## 1. 文件说明

| 文件 | 内容 | 端口 |
|------|------|------|
| `01_hello.py` | 最小应用：@app.get + async 函数，纯文本与 JSON 响应 | 8021 |
| `02_routing.py` | 路由：路径参数、查询参数、GET/POST/PUT/DELETE | 8022 |
| `03_request_response.py` | 请求响应：JSON body、Header、自定义状态码/响应头 | 8023 |
| `04_pydantic_depends.py` | Pydantic 校验 + Depends 依赖注入 + /docs 文档 | 8024 |
| `05_response_model.py` | 响应模型：过滤敏感字段（输入带密码、输出不带） | 8025 |
| `06_form_cookie.py` | 表单提交 + Cookie 读写 | 8026 |
| `07_exception_handler.py` | 自定义异常处理：统一错误格式 | 8027 |
| `08_router_structure.py` | APIRouter：多文件拆分路由、prefix、tags | 8028 |
| `09_middleware.py` | 中间件：CORS 跨域、请求计时 | 8029 |
| `10_file.py` | 文件上传（UploadFile）/ 下载（FileResponse） | 8030 |
| `11_testing.py` | pytest + TestClient：不起服务器的测试 | - |
| `12_database.py` | SQLAlchemy + CRUD：完整增删改查 | 8032 |
| `13_background_task.py` | BackgroundTasks：后台异步任务 | 8033 |
| `14_auth.py` | JWT 鉴权：注册→登录→token→受保护接口 | 8034 |
| `15_lifespan.py` | 生命周期：启动初始化 / 关闭清理 | 8035 |
| `16_websocket.py` | WebSocket：实时双向通信 | 8036 |
| `17_deploy.py` | 生产部署：uvicorn/Gunicorn/Docker/HTTPS | 8037 |
| `clients/` | 每个配方的 requests 请求脚本（Python 版 curl） | - |
| `_curl_selftest.py` | 【工具】起服务 + 真实 curl 自测助手 | - |

## 2. 运行方式

```bash
# 方式一：自测（起服务 + curl 打一遍 + 关服务）
python 01_hello.py

# 方式二：起服务，手动测试
python 01_hello.py --serve
# 另开终端用 requests 脚本测试：
python clients/01_hello.py
# 或浏览器打开 http://127.0.0.1:8021/docs 看交互文档
```

## 3. 学习路线

```
入门基础                    中间层                      生产级
─────────                  ─────────                  ─────────
01 最小应用                 05 响应模型                  12 数据库 CRUD
02 路由参数                 06 表单 Cookie               13 后台任务
03 请求响应                 07 异常处理                  14 JWT 鉴权
04 Pydantic 校验            08 APIRouter 拆分            15 生命周期
                           09 中间件 CORS               16 WebSocket
                           10 文件上传下载               17 部署配置
                           11 测试
```

## 4. 适用 / 不适用

| 场景 | 推荐 |
|------|------|
| REST API、微服务、后端接口 | ✅ 当下最推荐 |
| 需要请求数据校验（Pydantic） | ✅ 自动校验 + 422 |
| 需要自动 API 文档（/docs） | ✅ 零额外代码 |
| I/O 密集、高并发（async） | ✅ 原生支持 |
| 传统服务端渲染页面 | ⚠️ Flask/Django 更顺手 |
| 团队不用类型注解 | ⚠️ 优势发挥不出来 |

## 5. 核心速查

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
