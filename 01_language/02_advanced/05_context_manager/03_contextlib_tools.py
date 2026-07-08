"""contextlib 工具 + 异步上下文管理器

Python 3.12。
运行: python 03_contextlib_tools.py

contextlib 提供了一组辅助工具，让"资源管理"更灵活：
  suppress       —— 静默指定异常
  ExitStack      —— 动态注册任意数量的上下文管理器
  nullcontext    —— 条件性 with 时的占位符
  closing        —— 把任意有 close() 的对象包装成 CM
  asynccontextmanager —— @contextmanager 的异步版
  AbstractContextManager / AbstractAsyncContextManager —— 基类

演示：
  ① suppress：静默指定异常
  ② ExitStack：动态注册多个 CM
  ③ ExitStack 作为资源组 + 回调
  ④ nullcontext：条件性 with
  ⑤ closing：包装只有 close() 的对象
  ⑥ async with + @asynccontextmanager
"""

import asyncio
import os
import tempfile
from contextlib import (
    suppress,
    ExitStack,
    nullcontext,
    closing,
    contextmanager,
    asynccontextmanager,
    AbstractContextManager,
)


# ---------------------------------------------------------------------------
# ① suppress
# ---------------------------------------------------------------------------

def demo01_suppress():
    """① suppress：静默指定异常，等价于 try/except: pass"""
    print("① suppress")

    # 传统写法
    try:
        os.remove("/tmp/nonexistent_file.txt")
    except FileNotFoundError:
        pass

    # suppress 写法：更简洁，意图更明确
    with suppress(FileNotFoundError):
        os.remove("/tmp/nonexistent_file.txt")
    print("  删除不存在文件后正常继续（FileNotFoundError 被 suppress）")

    # 可以同时 suppress 多个异常类型
    with suppress(FileNotFoundError, PermissionError):
        raise FileNotFoundError("示例")
    print("  多类型 suppress 正常工作")

    # suppress 不是万能的——只在确实无所谓时用
    # 不要用来吞掉所有异常：suppress(Exception) 是坏味道


# ---------------------------------------------------------------------------
# ② ExitStack：动态注册
# ---------------------------------------------------------------------------

def demo02_exitstack_dynamic():
    """② ExitStack：运行时动态决定打开哪些资源"""
    print("\n② ExitStack 动态注册")

    # 创建若干临时文件
    paths = []
    for i in range(3):
        f = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=f"_{i}.txt")
        f.write(f"文件 {i}")
        f.close()
        paths.append(f.name)

    try:
        # 动态注册——文件数量在运行时确定
        with ExitStack() as stack:
            handles = [stack.enter_context(open(p)) for p in paths]
            print(f"  打开了 {len(handles)} 个文件")
            for i, h in enumerate(handles):
                print(f"  文件{i}: {h.read()!r}")
        # 离开 with 块，所有文件自动关闭
        print(f"  全部关闭: {all(h.closed for h in handles)}")
    finally:
        for p in paths:
            os.unlink(p)


# ---------------------------------------------------------------------------
# ③ ExitStack 作为资源组 + 回调
# ---------------------------------------------------------------------------

def demo03_exitstack_callback():
    """③ ExitStack.callback：注册任意清理函数"""
    print("\n③ ExitStack + callback")

    def cleanup(label: str):
        print(f"  [cleanup] {label}")

    with ExitStack() as stack:
        # 注册普通上下文管理器
        stack.enter_context(suppress(Exception))

        # 注册清理回调（任意函数）
        stack.callback(cleanup, "回调A")
        stack.callback(cleanup, "回调B")

        print("  with 块内正常执行")
        # 离开时按 LIFO 顺序执行：回调B → 回调A

    # ExitStack.pop_all()：把所有注册的 CM 转移出去（延迟清理）
    outer = ExitStack()
    inner = ExitStack()
    inner.callback(cleanup, "转移回调")
    inner.pop_all().close  # 转移到 outer（此处简化演示）
    outer.close()


# ---------------------------------------------------------------------------
# ④ nullcontext
# ---------------------------------------------------------------------------

def demo04_nullcontext():
    """④ nullcontext：条件性 with 的占位符"""
    print("\n④ nullcontext")

    def process(data: list, lock=None):
        """lock 可选——有锁用锁，没锁用 nullcontext 占位"""
        cm = lock if lock is not None else nullcontext()
        with cm:
            return sum(data)

    import threading

    real_lock = threading.Lock()

    # 有锁
    result1 = process([1, 2, 3, 4], lock=real_lock)
    print(f"  有锁结果: {result1}")

    # 无锁（nullcontext 当占位符，代码结构不变）
    result2 = process([1, 2, 3, 4])
    print(f"  无锁结果: {result2}")

    # Python 3.10+ nullcontext 支持 enter_result 参数
    with nullcontext("占位对象") as obj:
        print(f"  nullcontext as: {obj!r}")


# ---------------------------------------------------------------------------
# ⑤ closing
# ---------------------------------------------------------------------------

class FakeSocket:
    """模拟只有 close() 方法但没有实现 CM 协议的对象"""

    def __init__(self, host: str):
        self.host = host
        print(f"  [Socket] 连接到 {host}")

    def recv(self) -> bytes:
        return b"data"

    def close(self):
        print(f"  [Socket] 断开 {self.host}")


def demo05_closing():
    """⑤ closing：把有 close() 的对象包装成上下文管理器"""
    print("\n⑤ closing")

    with closing(FakeSocket("example.com:80")) as sock:
        data = sock.recv()
        print(f"  收到: {data!r}")
    # 离开时自动调用 sock.close()


# ---------------------------------------------------------------------------
# ⑥ async with + @asynccontextmanager
# ---------------------------------------------------------------------------

@asynccontextmanager
async def async_managed_connection(url: str):
    """异步上下文管理器：连接异步数据库"""
    print(f"  [AsyncCM] 建立连接: {url}")
    await asyncio.sleep(0.01)           # 模拟异步连接
    try:
        yield {"url": url, "connected": True}
    finally:
        await asyncio.sleep(0.01)       # 模拟异步关闭
        print(f"  [AsyncCM] 关闭连接: {url}")


@asynccontextmanager
async def async_transaction(conn: dict):
    """异步事务"""
    print("  [AsyncTx] BEGIN")
    try:
        yield conn
        print("  [AsyncTx] COMMIT")
    except Exception as e:
        print(f"  [AsyncTx] ROLLBACK ({e})")
        raise


async def demo06_async_cm():
    """⑥ async with + @asynccontextmanager"""
    print("\n⑥ 异步上下文管理器")

    # 单个 async with
    async with async_managed_connection("postgresql://localhost/mydb") as conn:
        print(f"  连接对象: {conn}")

    # 嵌套 async with（模拟事务）
    print()
    async with async_managed_connection("postgresql://localhost/mydb") as conn:
        async with async_transaction(conn) as tx:
            print(f"  在事务内执行 SQL: SELECT 1")

    # 失败回滚
    print()
    try:
        async with async_managed_connection("postgresql://localhost/mydb") as conn:
            async with async_transaction(conn) as tx:
                raise RuntimeError("业务异常")
    except RuntimeError:
        print("  RuntimeError 在外部被捕获")


async def async_main():
    await demo06_async_cm()


if __name__ == "__main__":
    demo01_suppress()
    demo02_exitstack_dynamic()
    demo03_exitstack_callback()
    demo04_nullcontext()
    demo05_closing()
    asyncio.run(async_main())
