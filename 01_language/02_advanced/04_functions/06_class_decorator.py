"""类装饰器 —— __call__ / 装饰类自身

Python 3.12。
运行: python 06_class_decorator.py

类装饰器有两种含义：
  A. 用类实现装饰器（类替代闭包，__init__ 接收函数，__call__ 包装调用）
  B. 装饰器作用于类（接收类，返回修改后的类）

演示：
  ① 类实现装饰器（无参）
  ② 类实现带参装饰器
  ③ 类装饰器 vs 函数装饰器的区别（__get__ / 方法绑定问题）
  ④ 装饰类自身 A：自动添加 __repr__
  ⑤ 装饰类自身 B：单例模式
  ⑥ 装饰类自身 C：注册插件
"""

import functools


# ---------------------------------------------------------------------------
# ① 类实现装饰器（无参）
# ---------------------------------------------------------------------------

class CallCounter:
    """记录函数被调用次数的装饰器（类实现）"""

    def __init__(self, func):
        functools.update_wrapper(self, func)  # 等价于 @wraps，复制元信息
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"  [{self.func.__name__}] 第 {self.count} 次调用")
        return self.func(*args, **kwargs)


@CallCounter
def greet(name: str) -> str:
    return f"你好，{name}！"


def demo01_class_as_decorator():
    """① 类实现无参装饰器"""
    print("① 类实现无参装饰器")
    print(f"  {greet('Alice')}")
    print(f"  {greet('Bob')}")
    print(f"  {greet('Carol')}")
    print(f"  greet 被调用了 {greet.count} 次")    # 类实例有 .count 属性！


# ---------------------------------------------------------------------------
# ② 类实现带参装饰器
# ---------------------------------------------------------------------------

class RateLimit:
    """限速装饰器：每秒最多调用 N 次（简化版，不精确计时）"""

    def __init__(self, max_calls: int):
        self.max_calls = max_calls
        self._calls_this_second = 0

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self._calls_this_second += 1
            if self._calls_this_second > self.max_calls:
                raise RuntimeError(
                    f"{func.__name__} 超过速率限制 "
                    f"（{self._calls_this_second}/{self.max_calls}）"
                )
            return func(*args, **kwargs)
        return wrapper


@RateLimit(max_calls=2)
def api_call(endpoint: str) -> str:
    return f"响应: {endpoint}"


def demo02_class_with_args():
    """② 类实现带参装饰器"""
    print("\n② 类实现带参装饰器（限速）")
    for i in range(4):
        try:
            result = api_call(f"/api/v{i}")
            print(f"  {result}")
        except RuntimeError as e:
            print(f"  被限速: {e}")


# ---------------------------------------------------------------------------
# ③ 方法绑定问题（类装饰器 vs 函数装饰器）
# ---------------------------------------------------------------------------

class TraceClass:
    """用于装饰类方法的装饰器类——需要实现 __get__ 才能正确绑定 self"""

    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func

    def __call__(self, *args, **kwargs):
        print(f"  [trace] {self.func.__name__} 被调用")
        return self.func(*args, **kwargs)

    def __get__(self, obj, objtype=None):
        # 实现描述符协议，使 self 能正确绑定到实例方法
        if obj is None:
            return self
        return functools.partial(self, obj)


class MyService:
    @TraceClass
    def process(self, data: str) -> str:
        return data.upper()


def demo03_method_binding():
    """③ 类装饰器装饰实例方法：需要 __get__ 支持描述符协议"""
    print("\n③ 类装饰器 + 实例方法")
    svc = MyService()
    result = svc.process("hello")
    print(f"  结果: {result}")


# ---------------------------------------------------------------------------
# ④ 装饰类自身：自动添加 __repr__
# ---------------------------------------------------------------------------

def auto_repr(cls):
    """给类自动添加 __repr__，展示所有 __init__ 参数"""
    def __repr__(self):
        attrs = vars(self)
        parts = ", ".join(f"{k}={v!r}" for k, v in attrs.items())
        return f"{type(self).__name__}({parts})"
    cls.__repr__ = __repr__
    return cls


@auto_repr
class Point:
    def __init__(self, x: float, y: float, label: str = ""):
        self.x = x
        self.y = y
        self.label = label


@auto_repr
class Color:
    def __init__(self, r: int, g: int, b: int):
        self.r = r
        self.g = g
        self.b = b


def demo04_auto_repr():
    """④ 装饰类：自动 __repr__"""
    print("\n④ 装饰类：auto_repr")
    p = Point(3.0, 4.0, label="A")
    c = Color(255, 128, 0)
    print(f"  {p}")
    print(f"  {c}")


# ---------------------------------------------------------------------------
# ⑤ 装饰类：单例模式
# ---------------------------------------------------------------------------

def singleton(cls):
    """单例装饰器：同一个类只能有一个实例"""
    instances: dict = {}

    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class DatabaseConnection:
    def __init__(self, url: str):
        self.url = url
        print(f"  [DB] 建立连接: {url}")


def demo05_singleton():
    """⑤ 装饰类：单例"""
    print("\n⑤ 单例装饰器")
    db1 = DatabaseConnection("postgresql://localhost:5432/mydb")
    db2 = DatabaseConnection("sqlite:///other.db")   # 不会再建连接，返回已有实例
    print(f"  db1 is db2: {db1 is db2}")
    print(f"  url: {db1.url}")


# ---------------------------------------------------------------------------
# ⑥ 装饰类：插件注册
# ---------------------------------------------------------------------------

_HANDLERS: dict = {}


def register(event_name: str):
    """把类注册为某个事件的处理器"""
    def decorator(cls):
        _HANDLERS[event_name] = cls
        return cls
    return decorator


@register("order.created")
class OrderCreatedHandler:
    def handle(self, payload: dict):
        print(f"  [OrderCreated] 订单: {payload}")


@register("user.signup")
class UserSignupHandler:
    def handle(self, payload: dict):
        print(f"  [UserSignup] 用户: {payload}")


def dispatch(event_name: str, payload: dict):
    handler_cls = _HANDLERS.get(event_name)
    if handler_cls:
        handler_cls().handle(payload)
    else:
        print(f"  未知事件: {event_name!r}")


def demo06_plugin_registry():
    """⑥ 装饰类：插件注册表"""
    print("\n⑥ 插件注册")
    print(f"  已注册处理器: {list(_HANDLERS.keys())}")
    dispatch("order.created", {"id": 42, "amount": 99.9})
    dispatch("user.signup", {"username": "alice"})
    dispatch("payment.failed", {})


if __name__ == "__main__":
    demo01_class_as_decorator()
    demo02_class_with_args()
    demo03_method_binding()
    demo04_auto_repr()
    demo05_singleton()
    demo06_plugin_registry()
