"""
11_testing.py —— pytest + TestClient：不起服务器的测试
================================================================================
所属: 三方库 FastAPI | Python 3.12 | 额外: pip install pytest httpx

运行:
  python 11_testing.py         # 直接跑，看测试结果
  pytest 11_testing.py -v      # 用 pytest 跑（推荐）

要点:
  ① TestClient —— 不起真实服务器，直接在内存里调 ASGI 应用
  ② 测 JSON 响应 —— client.get/post 返回 Response 对象，.json() 取 body
  ③ 测状态码 —— response.status_code
  ④ 测错误场景 —— 422 / 404 等

  TestClient 底层用 httpx，和 requests 的 API 几乎一样。
================================================================================
"""

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

# ── 被测试的 app ──
app = FastAPI()


class Item(BaseModel):
    name: str
    price: float = Field(gt=0)


ITEMS: dict[int, dict] = {}


@app.post("/item", status_code=201)
async def create_item(item: Item):
    new_id = len(ITEMS) + 1
    ITEMS[new_id] = {"id": new_id, **item.model_dump()}
    return ITEMS[new_id]


@app.get("/item/{item_id}")
async def get_item(item_id: int):
    if item_id not in ITEMS:
        raise HTTPException(status_code=404, detail="not found")
    return ITEMS[item_id]


# ── 测试代码 ──
# ① TestClient 不起真实服务器，直接调 ASGI app
client = TestClient(app)


def test_create_item():
    """② 测 POST + JSON body + 201 状态码。"""
    resp = client.post("/item", json={"name": "手机", "price": 999})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "手机"
    assert data["price"] == 999
    assert "id" in data
    print(f"  ✓ 创建成功: {data}")


def test_get_item():
    """③ 测 GET + 200。"""
    resp = client.get("/item/1")
    assert resp.status_code == 200
    assert resp.json()["name"] == "手机"
    print(f"  ✓ 查询成功: {resp.json()}")


def test_not_found():
    """④ 测 404 错误场景。"""
    resp = client.get("/item/999")
    assert resp.status_code == 404
    print(f"  ✓ 404 正确: {resp.json()}")


def test_validation_error():
    """⑤ 测 422 校验失败（price=-1 违反 gt=0）。"""
    resp = client.post("/item", json={"name": "错误", "price": -1})
    assert resp.status_code == 422
    print(f"  ✓ 422 正确: 校验拦截了 price=-1")


if __name__ == "__main__":
    print("=" * 50)
    print("TestClient 测试（不起服务器，内存里直接调 app）")
    print("=" * 50)
    ITEMS.clear()
    test_create_item()
    test_get_item()
    test_not_found()
    test_validation_error()
    print("\n全部通过")
