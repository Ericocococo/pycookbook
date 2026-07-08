"""异步生成器 —— async def + yield

Python 3.12。
运行: python 05_async_generator.py

异步生成器 = async def 函数体中含 yield 表达式。
用 async for 消费，不能用普通 for。
不能有 return <value>（只能裸 return 或无 return）。

演示：
  ① 最简异步生成器
  ② 自定义异步迭代器（__aiter__ / __anext__）
  ③ 异步生成器表达式
  ④ aclose() 与 finally 清理
  ⑤ 实际场景：模拟异步分页拉取
"""

import asyncio


# ---------------------------------------------------------------------------
# ① 最简异步生成器
# ---------------------------------------------------------------------------

async def async_range(n: int):
    """异步版 range，每次 yield 前模拟 I/O 等待"""
    for i in range(n):
        await asyncio.sleep(0)           # 让出事件循环（模拟异步 I/O）
        yield i


async def demo01_basic():
    """① async for 消费异步生成器"""
    print("① 最简异步生成器")

    values = []
    async for val in async_range(5):
        values.append(val)
    print(f"  收集结果: {values}")

    # aiter() / anext() 是手动驱动的方式（等价于 iter/next）
    gen = async_range(3)
    v = await anext(gen)
    print(f"  anext(): {v}")
    await gen.aclose()                   # 主动关闭，触发 finally


# ---------------------------------------------------------------------------
# ② 自定义异步迭代器（协议）
# ---------------------------------------------------------------------------

class AsyncCounter:
    """手写异步迭代器：实现 __aiter__ 和 __anext__"""

    def __init__(self, stop: int):
        self._stop = stop
        self._current = 0

    def __aiter__(self):
        return self                      # 返回自身

    async def __anext__(self) -> int:
        if self._current >= self._stop:
            raise StopAsyncIteration     # 异步版 StopIteration
        await asyncio.sleep(0)
        value = self._current
        self._current += 1
        return value


async def demo02_custom_aiterator():
    """② 手写异步迭代器 AsyncCounter"""
    print("\n② 自定义异步迭代器")

    total = 0
    async for n in AsyncCounter(5):
        total += n
    print(f"  0+1+2+3+4 = {total}")


# ---------------------------------------------------------------------------
# ③ 异步生成器表达式
# ---------------------------------------------------------------------------

async def demo03_async_genexpr():
    """③ 异步生成器表达式：(expr async for x in async_iter)"""
    print("\n③ 异步生成器表达式")

    # 把每个值平方（异步推导式）
    squared = [x * x async for x in async_range(5)]
    print(f"  平方结果: {squared}")

    # 带过滤
    evens = [x async for x in async_range(10) if x % 2 == 0]
    print(f"  偶数:     {evens}")


# ---------------------------------------------------------------------------
# ④ aclose() 与 finally 清理
# ---------------------------------------------------------------------------

async def resource_gen():
    """模拟持有资源的异步生成器"""
    print("  [gen] 资源打开")
    try:
        for i in range(100):
            await asyncio.sleep(0)
            yield i
    except GeneratorExit:
        # aclose() 会注入 GeneratorExit（与同步生成器一致）
        print("  [gen] 收到 GeneratorExit")
    finally:
        print("  [gen] 资源释放（finally 保证执行）")


async def demo04_aclose():
    """④ aclose() 提前关闭，finally 保证清理"""
    print("\n④ aclose() 清理")

    gen = resource_gen()
    print("  取前 3 个:")
    count = 0
    async for val in gen:
        print(f"  {val}", end="  ")
        count += 1
        if count >= 3:
            break
    print()
    await gen.aclose()                   # 显式关闭，触发 finally


# ---------------------------------------------------------------------------
# ⑤ 实际场景：模拟异步分页拉取
# ---------------------------------------------------------------------------

async def fetch_page(page: int, size: int = 3) -> list[dict]:
    """模拟从 API 分页拉取数据（真实场景用 aiohttp）"""
    await asyncio.sleep(0.01)            # 模拟网络延迟
    start = page * size
    return [{"id": start + i, "value": (start + i) * 10} for i in range(size)]


async def paginated_items(total_pages: int):
    """异步生成器：逐页拉取，逐条 yield，调用方不感知分页"""
    for page in range(total_pages):
        items = await fetch_page(page)
        for item in items:
            yield item


async def demo05_pagination():
    """⑤ 实际场景：异步分页拉取，对调用方透明"""
    print("\n⑤ 异步分页拉取（3 页 × 每页 3 条）")

    async for item in paginated_items(total_pages=3):
        print(f"  id={item['id']:2d}  value={item['value']}")


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

async def main():
    await demo01_basic()
    await demo02_custom_aiterator()
    await demo03_async_genexpr()
    await demo04_aclose()
    await demo05_pagination()


if __name__ == "__main__":
    asyncio.run(main())
