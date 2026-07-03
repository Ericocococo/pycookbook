"""反射 —— __getattr__ / __getattribute__ / __setattr__ / __delattr__

Python 3.12。
运行: python 03_magic_attrs.py

这四个魔法方法让你控制"属性访问"这件事本身的行为，
是实现代理、懒加载、ORM-like API、只读对象的基础手段。

关键区别：
  __getattr__        仅在"找不到属性"时触发（兜底钩子）
  __getattribute__   每次属性访问都触发（必须小心无限递归）
  __setattr__        每次属性赋值都触发
  __delattr__        每次 del obj.attr 都触发

演示：
  ① __getattr__：懒加载 / 属性代理
  ② __getattr__ vs __getattribute__：触发时机对比
  ③ __setattr__：拦截赋值（类型校验 / 只读保护）
  ④ __delattr__：拦截删除
  ⑤ 综合场景 A：属性代理（把访问转发给内部对象）
  ⑥ 综合场景 B：点号访问的 dict（类 JavaScript 风格）
"""


# ---------------------------------------------------------------------------
# ① __getattr__：兜底钩子
# ---------------------------------------------------------------------------

def demo01_getattr_hook():
    """① __getattr__：找不到属性时的兜底

    查找顺序（简化版）：
      1. 实例 __dict__
      2. 类 __dict__ 及其 MRO
      3. 以上都找不到 → 调用 __getattr__
      4. __getattr__ 也没有或抛 AttributeError → 报错

    用途：懒计算属性、属性名模糊匹配、代理转发。
    """
    print("① __getattr__ 兜底钩子")

    class LazyConfig:
        def __init__(self):
            self._data = {"host": "localhost", "port": 5432}

        def __getattr__(self, name):
            # 只在找不到属性时才来这里
            if name in self._data:
                return self._data[name]
            raise AttributeError(f"没有配置项: {name!r}")

    cfg = LazyConfig()
    print("  cfg.host:", cfg.host)       # 触发 __getattr__
    print("  cfg.port:", cfg.port)       # 触发 __getattr__
    print("  cfg._data 直接访问:", cfg._data)   # 不触发（在 __dict__ 里能找到）

    try:
        _ = cfg.timeout
    except AttributeError as e:
        print("  不存在的配置:", e)


# ---------------------------------------------------------------------------
# ② __getattr__ vs __getattribute__ 触发时机
# ---------------------------------------------------------------------------

def demo02_getattr_vs_getattribute():
    """② __getattr__ vs __getattribute__ 对比

    __getattribute__ 是"属性访问协议"的实际执行者，
    每次 obj.anything 都会经过它，包括 obj.__dict__、obj.__class__。

    在 __getattribute__ 里访问 self.xxx 会再次触发自身 → 无限递归！
    正确做法：用 object.__getattribute__(self, name) 绕过，或用 self.__dict__[name]。
    """
    print("\n② __getattr__ vs __getattribute__")

    class Watcher:
        def __init__(self):
            self.x = 1
            self.y = 2

        def __getattr__(self, name):
            print(f"    [__getattr__] 找不到: {name!r}")
            raise AttributeError(name)

        def __getattribute__(self, name):
            print(f"    [__getattribute__] 访问: {name!r}")
            # 必须用 object.__getattribute__ 来实际读取，否则无限递归
            return object.__getattribute__(self, name)

    print("  访问 obj.x（存在的属性）:")
    w = Watcher()
    _ = w.x   # 只触发 __getattribute__，不触发 __getattr__

    print("  访问 obj.z（不存在的属性）:")
    try:
        _ = w.z   # 先触发 __getattribute__，找不到后触发 __getattr__
    except AttributeError:
        pass

    print("  结论：__getattr__ 只在找不到时触发，__getattribute__ 每次都触发")


# ---------------------------------------------------------------------------
# ③ __setattr__：拦截赋值
# ---------------------------------------------------------------------------

def demo03_setattr_hook():
    """③ __setattr__：拦截所有属性赋值

    每次 obj.name = value 都会触发，包括 __init__ 里的 self.x = ...
    所以在 __setattr__ 里不能直接 self.x = value（无限递归），
    必须用 object.__setattr__(self, name, value) 或 self.__dict__[name] = value。

    用途：类型校验、值范围检查、只读属性保护。
    """
    print("\n③ __setattr__ 拦截赋值")

    class TypedPoint:
        """只接受数字坐标的点，拦截非数字赋值"""
        def __init__(self, x, y):
            self.x = x    # 会触发 __setattr__
            self.y = y

        def __setattr__(self, name, value):
            if name in ("x", "y") and not isinstance(value, (int, float)):
                raise TypeError(f"{name} 必须是数字，收到 {type(value).__name__!r}")
            # 正确写法：调用 object 的实现，避免递归
            object.__setattr__(self, name, value)

    p = TypedPoint(1, 2)
    print("  p.x, p.y:", p.x, p.y)

    p.x = 3.14   # 合法
    print("  修改后 p.x:", p.x)

    try:
        p.x = "hello"   # 非法
    except TypeError as e:
        print("  非法赋值:", e)


# ---------------------------------------------------------------------------
# ④ __delattr__：拦截删除
# ---------------------------------------------------------------------------

def demo04_delattr_hook():
    """④ __delattr__：拦截 del obj.attr

    拦截删除操作，常用于：
      - 防止删除关键属性（只读保护）
      - 删除时做清理工作（资源释放）
    """
    print("\n④ __delattr__ 拦截删除")

    class Protected:
        READONLY = frozenset({"id", "created_at"})

        def __init__(self, id_):
            self.id = id_
            self.created_at = "2024-01-01"
            self.tag = "可删除"

        def __delattr__(self, name):
            if name in self.READONLY:
                raise AttributeError(f"{name!r} 是只读属性，不允许删除")
            print(f"    删除属性: {name!r}")
            object.__delattr__(self, name)

    obj = Protected(42)

    del obj.tag          # 合法
    print("  删除 tag 成功")

    try:
        del obj.id       # 受保护
    except AttributeError as e:
        print("  删除 id 失败:", e)


# ---------------------------------------------------------------------------
# ⑤ 综合场景 A：属性代理
# ---------------------------------------------------------------------------

def demo05_proxy():
    """⑤ 属性代理：把点号访问转发给内部对象

    代理模式：外层对象暴露与内层相同的接口，
    但可以在转发前后加日志、权限检查、缓存等。
    """
    print("\n⑤ 属性代理")

    class LoggingProxy:
        """给任意对象套一层日志，记录每次属性访问"""
        def __init__(self, target):
            # 直接写 self._target = target 会触发自定义 __setattr__，
            # 所以用 object.__setattr__ 绕过
            object.__setattr__(self, "_target", target)

        def __getattr__(self, name):
            target = object.__getattribute__(self, "_target")
            value = getattr(target, name)
            print(f"    [proxy] 访问 .{name} → {value!r}")
            return value

        def __setattr__(self, name, value):
            target = object.__getattribute__(self, "_target")
            print(f"    [proxy] 设置 .{name} = {value!r}")
            setattr(target, name, value)

    class Model:
        def __init__(self):
            self.name = "Alice"
            self.age = 30

    m = Model()
    proxy = LoggingProxy(m)
    print("  读取 name:", proxy.name)
    proxy.age = 31
    print("  m.age 实际值:", m.age)


# ---------------------------------------------------------------------------
# ⑥ 综合场景 B：点号访问的 dict
# ---------------------------------------------------------------------------

def demo06_dot_dict():
    """⑥ 点号访问的 dict（AttrDict）

    让 d["key"] 和 d.key 等价。
    常见于配置对象、API 响应解析。

    实现要点：
      - 继承 dict，存储仍在 dict 里
      - __getattr__ 把属性访问转给 dict 的键
      - __setattr__ 把属性赋值转给 dict 的键
    """
    print("\n⑥ AttrDict：点号访问的字典")

    class AttrDict(dict):
        def __getattr__(self, name):
            try:
                return self[name]
            except KeyError:
                raise AttributeError(name)

        def __setattr__(self, name, value):
            self[name] = value

        def __delattr__(self, name):
            try:
                del self[name]
            except KeyError:
                raise AttributeError(name)

    config = AttrDict(host="localhost", port=5432)
    print("  config['host']:", config["host"])
    print("  config.host:", config.host)      # 等价

    config.debug = True                        # 等价于 config["debug"] = True
    print("  config:", dict(config))

    del config.port
    print("  删除 port 后:", dict(config))


if __name__ == "__main__":
    demo01_getattr_hook()
    demo02_getattr_vs_getattribute()
    demo03_setattr_hook()
    demo04_delattr_hook()
    demo05_proxy()
    demo06_dot_dict()
