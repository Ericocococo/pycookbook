"""
12_database.py —— SQLAlchemy + CRUD：数据库接入
================================================================================
所属: 三方库 FastAPI + SQLAlchemy 2.0 | Python 3.12
安装: pip install sqlalchemy

运行:
  python 12_database.py         # 自测（用内存 SQLite，不需要装数据库）
  python 12_database.py --serve  # 起服务

要点:
  ① create_engine + SQLite 内存库 —— 开发自测不需要装 MySQL/PG
  ② DeclarativeBase + Mapped —— SQLAlchemy 2.0 新写法定义表
  ③ Depends(get_db) —— 用依赖注入管理 Session 生命周期
  ④ CRUD 四个接口 —— 增删改查完整流程
================================================================================
"""

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, String
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

PORT = 8032
app = FastAPI()

# ── ① 数据库连接（SQLite 内存库，重启清空） ──
engine = create_engine("sqlite:///:memory:", echo=False)
SessionLocal = sessionmaker(bind=engine)


# ── ② 定义表（SQLAlchemy 2.0 写法） ──
class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    age: Mapped[int] = mapped_column()


Base.metadata.create_all(engine)


# ── Pydantic 模型（和 SQLAlchemy 模型分开） ──
class UserCreate(BaseModel):
    name: str
    age: int = Field(gt=0, le=150)


class UserOut(BaseModel):
    id: int
    name: str
    age: int
    model_config = {"from_attributes": True}


# ── ③ 依赖注入：管理 Session ──
def get_db():
    """每个请求一个 Session，请求结束自动关闭。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── ④ CRUD 接口 ──
@app.post("/user", response_model=UserOut, status_code=201)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """增：创建用户。"""
    row = UserModel(name=user.name, age=user.age)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.get("/user/{uid}", response_model=UserOut)
async def get_user(uid: int, db: Session = Depends(get_db)):
    """查：按 id 查用户。"""
    row = db.get(UserModel, uid)
    if not row:
        raise HTTPException(status_code=404, detail=f"用户 {uid} 不存在")
    return row


@app.get("/users", response_model=list[UserOut])
async def list_users(db: Session = Depends(get_db)):
    """查：列出所有用户。"""
    return db.query(UserModel).all()


@app.put("/user/{uid}", response_model=UserOut)
async def update_user(uid: int, user: UserCreate, db: Session = Depends(get_db)):
    """改：更新用户。"""
    row = db.get(UserModel, uid)
    if not row:
        raise HTTPException(status_code=404, detail=f"用户 {uid} 不存在")
    row.name = user.name
    row.age = user.age
    db.commit()
    db.refresh(row)
    return row


@app.delete("/user/{uid}")
async def delete_user(uid: int, db: Session = Depends(get_db)):
    """删：删除用户。"""
    row = db.get(UserModel, uid)
    if not row:
        raise HTTPException(status_code=404, detail=f"用户 {uid} 不存在")
    db.delete(row)
    db.commit()
    return {"deleted": uid}


CURL_CASES = [
    {"desc": "创建用户", "method": "POST", "path": "/user",
     "json": {"name": "张三", "age": 25}},
    {"desc": "创建第二个", "method": "POST", "path": "/user",
     "json": {"name": "李四", "age": 30}},
    {"desc": "查单个", "path": "/user/1"},
    {"desc": "查列表", "path": "/users"},
    {"desc": "更新", "method": "PUT", "path": "/user/1",
     "json": {"name": "张三改", "age": 26}},
    {"desc": "删除", "method": "DELETE", "path": "/user/2"},
    {"desc": "查列表（删后）", "path": "/users"},
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
