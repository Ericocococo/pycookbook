"""反射 —— getattr / setattr / delattr / hasattr 四件套

Python 3.12。
运行: python 01_getattr_family.py

普通属性访问：obj.name（编译时确定）
反射属性访问：getattr(obj, "name")（运行时字符串决定）

两者在语义上完全等价，反射的价值在于属性名可以是变量、配置、用户输入。

演示：
  ① getattr：基础读取，以及 default 参数（最重要）
  ② setattr：动态写入属性
  ③ delattr：动态删除属性
  ④ hasattr：检查属性是否存在（以及为什么它不可靠）
  ⑤ 实际场景 A：命令分发器（根据字符串名称调用方法）
  ⑥ 实际场景 B：字典 → 对象属性映射
"""


class Config:
    host = "localhost"
    port = 8080
    debug = False

    def __init__(self):
        self.name = "default"


class Robot:
    def go(self):    return "前进"
    def stop(self):  return "停止"
    def turn(self):  return "转弯"
    def status(self): return "状态正常"


# ---------------------------------------------------------------------------
# ① getattr
# ---------------------------------------------------------------------------

def demo01_getattr():
    """① getattr：动态读取属性

    getattr(obj, name)          等价于 obj.name，找不到抛 AttributeError
    getattr(obj, name, default) 找不到时返回 default，不抛异常

    第三个参数 default 非常重要——它让 getattr 变成"带兜底的安全读取"。
    """
    print("① getattr")

    cfg = Config()

    # 等价于 cfg.host
    print("  cfg.host:", getattr(cfg, "host"))

    # 属性名来自变量——这是反射的核心价值
    field = "port"
    print(f"  cfg.{field}:", getattr(cfg, field))

    # default 参数：找不到属性时返回默认值，而不是崩溃
    print("  不存在的字段（有 default）:", getattr(cfg, "timeout", 30))

    # 不带 default 且属性不存在：抛 AttributeError
    try:
        getattr(cfg, "nonexistent")
    except AttributeError as e:
        print("  不存在且无 default：", e)

    # 读取方法也可以——getattr 返回绑定方法对象
    method = getattr(cfg, "__class__")
    print("  getattr 读取类:", method)


# ---------------------------------------------------------------------------
# ② setattr
# ---------------------------------------------------------------------------

def demo02_setattr():
    """② setattr：动态写入属性

    setattr(obj, name, value) 等价于 obj.name = value
    能创建新属性，也能覆盖已有属性。
    """
    print("\n② setattr")

    cfg = Config()
    print("  修改前 host:", cfg.host)

    # 修改已有属性
    setattr(cfg, "host", "192.168.1.1")
    print("  修改后 host:", cfg.host)

    # 创建新属性（原来没有）
    setattr(cfg, "timeout", 30)
    print("  新增 timeout:", cfg.timeout)

    # 批量从字典设置属性（常见模式）
    updates = {"host": "10.0.0.1", "port": 9090, "debug": True}
    for key, value in updates.items():
        setattr(cfg, key, value)
    print("  批量更新后:", cfg.host, cfg.port, cfg.debug)


# ---------------------------------------------------------------------------
# ③ delattr
# ---------------------------------------------------------------------------

def demo03_delattr():
    """③ delattr：动态删除属性

    delattr(obj, name) 等价于 del obj.name
    只能删除实例属性，不能删除类属性（从实例上删）。
    """
    print("\n③ delattr")

    cfg = Config()
    cfg.extra = "临时字段"
    print("  删除前 extra:", cfg.extra)

    delattr(cfg, "extra")
    print("  删除后 hasattr extra:", hasattr(cfg, "extra"))

    # 删除不存在的属性：抛 AttributeError
    try:
        delattr(cfg, "nonexistent")
    except AttributeError as e:
        print("  删除不存在属性:", e)


# ---------------------------------------------------------------------------
# ④ hasattr
# ---------------------------------------------------------------------------

def demo04_hasattr():
    """④ hasattr：检查属性是否存在

    hasattr(obj, name) 内部实现是：
      try: getattr(obj, name); return True
      except AttributeError: return False

    这意味着：
      - 如果 __getattr__ 里抛了其他异常，hasattr 会把它当作"不存在"（Python 3.2 前的行为）
      - Python 3.2+ 只捕获 AttributeError，其他异常会向上传播
      - 更精确的写法是直接 try/getattr/except AttributeError
    """
    print("\n④ hasattr")

    cfg = Config()

    print("  hasattr host:", hasattr(cfg, "host"))        # True（类属性）
    print("  hasattr name:", hasattr(cfg, "name"))        # True（实例属性）
    print("  hasattr 不存在:", hasattr(cfg, "xyz"))       # False

    # hasattr 的常见用途：特性检测（duck typing）
    for obj in [cfg, "hello", 42, [1, 2, 3]]:
        has_len = hasattr(obj, "__len__")
        print(f"  {type(obj).__name__:8s} 有 __len__: {has_len}")


# ---------------------------------------------------------------------------
# ⑤ 实际场景 A：命令分发器
# ---------------------------------------------------------------------------

def demo05_command_dispatch():
    """⑤ 实际场景：命令分发器

    根据字符串命令名，动态调用对象上的方法。
    这是 getattr 最经典的用途，避免了大段 if/elif 链。
    """
    print("\n⑤ 命令分发器")

    robot = Robot()

    # 不用 getattr 的写法（冗长）：
    # if cmd == "go": robot.go()
    # elif cmd == "stop": robot.stop()
    # ...

    # 用 getattr 的写法（简洁，可扩展）：
    commands = ["go", "turn", "stop", "fly"]   # "fly" 不存在，测试兜底

    for cmd in commands:
        handler = getattr(robot, cmd, None)     # 找不到返回 None
        if handler is not None and callable(handler):
            result = handler()
            print(f"  {cmd}: {result}")
        else:
            print(f"  {cmd}: 未知命令，忽略")


# ---------------------------------------------------------------------------
# ⑥ 实际场景 B：字典 → 属性访问
# ---------------------------------------------------------------------------

def demo06_dict_to_attrs():
    """⑥ 实际场景：字典映射为属性访问风格

    配置通常以 dict 形式从 JSON/YAML 读入，但 cfg["host"] 不如 cfg.host 易读。
    用 setattr 把 dict 的键值对映射为对象属性，即可用点号访问。
    """
    print("\n⑥ 字典 → 属性映射")

    # 简单实现
    class Namespace:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

        def __repr__(self):
            return f"Namespace({vars(self)})"

    raw_config = {"host": "localhost", "port": 5432, "db": "mydb", "timeout": 10}
    cfg = Namespace(**raw_config)

    print("  cfg.host:", cfg.host)
    print("  cfg.port:", cfg.port)
    print("  repr:", cfg)

    # Python 标准库里的等价物：argparse.Namespace 就是这么实现的
    import argparse
    ns = argparse.Namespace(host="localhost", port=5432)
    print("  argparse.Namespace:", ns)
    print("  ns.host:", ns.host)


if __name__ == "__main__":
    demo01_getattr()
    demo02_setattr()
    demo03_delattr()
    demo04_hasattr()
    demo05_command_dispatch()
    demo06_dict_to_attrs()
