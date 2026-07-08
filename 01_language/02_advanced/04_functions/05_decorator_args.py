"""带参装饰器 —— 三层嵌套 / 可选参数

Python 3.12。
运行: python 05_decorator_args.py

带参装饰器比无参多一层：
  outer(param) → decorator(func) → wrapper(*a, **kw)

调用链：
  @repeat(3)
  def hello(): ...
  等价于：hello = repeat(3)(hello)

演示：
  ① 三层嵌套：最基本的带参装饰器
  ② 实用 demo A：带参重试（可配置次数和延迟）
  ③ 实用 demo B：权限控制
  ④ 实用 demo C：缓存（简化版，理解 functools.lru_cache 的原理）
  ⑤ 可选参数装饰器：@deco 和 @deco() 都能用
"""

import time
import functools


# ---------------------------------------------------------------------------
# ① 三层嵌套
# ---------------------------------------------------------------------------

def repeat(times: int):
    """重复调用函数 times 次的装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator


@repeat(3)
def say_hi(name: str):
    print(f"  嗨，{name}！")


def demo01_three_layer():
    """① 三层嵌套：带参装饰器"""
    print("① 三层嵌套")

    say_hi("Alice")

    # 手动等价：
    def hello():
        print("  hello!")
    hello_3x = repeat(3)(hello)         # repeat(3) 返回 decorator，再传入 hello
    hello_3x()


# ---------------------------------------------------------------------------
# ② 带参重试
# ---------------------------------------------------------------------------

def retry(max_attempts: int = 3, delay: float = 0.0,
          exceptions: tuple = (Exception,)):
    """可配置的重试装饰器

    Args:
        max_attempts: 最大尝试次数（含第一次）
        delay:        每次失败后等待秒数
        exceptions:   只重试这些异常类型
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    print(f"  [{func.__name__}] 第 {attempt}/{max_attempts} 次失败: {e}")
                    if attempt < max_attempts and delay > 0:
                        time.sleep(delay)
            raise last_exc
        return wrapper
    return decorator


_call_count = 0

@retry(max_attempts=4, exceptions=(ConnectionError,))
def unstable_request() -> str:
    global _call_count
    _call_count += 1
    if _call_count < 3:
        raise ConnectionError(f"超时（第 {_call_count} 次）")
    return "200 OK"


def demo02_retry():
    """② 带参重试"""
    print("\n② 带参重试")
    global _call_count
    _call_count = 0
    result = unstable_request()
    print(f"  最终结果: {result!r}")


# ---------------------------------------------------------------------------
# ③ 权限控制
# ---------------------------------------------------------------------------

# 模拟当前登录用户角色
CURRENT_USER_ROLE = "user"


def require_role(*allowed_roles: str):
    """权限装饰器：只允许指定角色调用"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if CURRENT_USER_ROLE not in allowed_roles:
                raise PermissionError(
                    f"{func.__name__} 需要角色 {allowed_roles}，"
                    f"当前角色: {CURRENT_USER_ROLE!r}"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator


@require_role("admin", "superuser")
def delete_user(user_id: int):
    print(f"  删除用户 {user_id}")


@require_role("user", "admin", "superuser")
def view_profile(user_id: int):
    print(f"  查看用户 {user_id} 的主页")


def demo03_permission():
    """③ 权限控制装饰器"""
    print("\n③ 权限控制")
    global CURRENT_USER_ROLE

    CURRENT_USER_ROLE = "user"
    view_profile(42)                    # 允许
    try:
        delete_user(42)                 # 被拦截
    except PermissionError as e:
        print(f"  PermissionError: {e}")

    CURRENT_USER_ROLE = "admin"
    delete_user(42)                     # 允许


# ---------------------------------------------------------------------------
# ④ 简化版缓存（理解 lru_cache 原理）
# ---------------------------------------------------------------------------

def simple_cache(maxsize: int = 128):
    """简化版缓存装饰器（不含 LRU 淘汰，仅演示原理）"""
    def decorator(func):
        cache: dict = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 把参数转成可哈希的 key
            key = (args, tuple(sorted(kwargs.items())))
            if key not in cache:
                if len(cache) >= maxsize:
                    # 简单策略：满了就清空（真实 LRU 更复杂）
                    cache.clear()
                    print(f"  [cache] 已满，清空")
                cache[key] = func(*args, **kwargs)
                print(f"  [cache] miss  → 计算 {func.__name__}{args}")
            else:
                print(f"  [cache] hit   → 命中 {func.__name__}{args}")
            return cache[key]

        wrapper.cache = cache           # 暴露 cache 供外部检查
        return wrapper
    return decorator


@simple_cache(maxsize=4)
def expensive(n: int) -> int:
    """模拟耗时计算"""
    return n * n


def demo04_cache():
    """④ 简化版缓存，理解 lru_cache 原理"""
    print("\n④ 简化版缓存")
    for n in [3, 5, 3, 7, 5, 9]:
        print(f"  expensive({n}) = {expensive(n)}")


# ---------------------------------------------------------------------------
# ⑤ 可选参数装饰器：@deco 和 @deco() 都能用
# ---------------------------------------------------------------------------

def optional_debug(func=None, *, verbose: bool = False):
    """可选参数装饰器——支持两种用法：
      @optional_debug
      @optional_debug(verbose=True)
    """
    # 如果直接作为 @optional_debug 使用（func 非 None）
    if func is None:
        # 作为 @optional_debug(...) 使用，返回真正的 decorator
        return functools.partial(optional_debug, verbose=verbose)

    # 此时 func 就是被装饰的函数
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if verbose:
            print(f"  [DEBUG] 调用 {func.__name__}{args} {kwargs}")
        result = func(*args, **kwargs)
        if verbose:
            print(f"  [DEBUG] 返回 {result!r}")
        return result
    return wrapper


@optional_debug
def add(a, b):
    return a + b


@optional_debug(verbose=True)
def mul(a, b):
    return a * b


def demo05_optional_args():
    """⑤ 可选参数：@deco 和 @deco() 都能用"""
    print("\n⑤ 可选参数装饰器")
    print(f"  add(1, 2) = {add(1, 2)}")    # 无 verbose，静默
    mul(3, 4)                               # verbose=True，打印调试


if __name__ == "__main__":
    demo01_three_layer()
    demo02_retry()
    demo03_permission()
    demo04_cache()
    demo05_optional_args()
