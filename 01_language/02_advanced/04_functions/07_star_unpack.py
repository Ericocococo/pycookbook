"""* 与 ** —— 收集与解包

Python 3.12。
运行: python 07_star_unpack.py

* 和 ** 在不同位置有不同含义：
  - 函数定义中：收集多余的位置参数 / 关键字参数
  - 函数调用中：把序列/字典展开为独立参数
  - 赋值语句中：捕获剩余元素
  - 字面量中：  合并序列或字典

演示：
  ① 函数定义：*args / **kwargs 收集参数
  ② 函数调用：* / ** 解包参数
  ③ 赋值解包：*rest 捕获剩余元素
  ④ 字面量合并：[*a, *b] / {**d1, **d2}
  ⑤ 仅限关键字参数（* 作分隔符）
  ⑥ 仅限位置参数（/ 作分隔符，Python 3.8+）
"""


# ---------------------------------------------------------------------------
# ① 函数定义：*args / **kwargs 收集参数
# ---------------------------------------------------------------------------

def demo01_collect():
    """① 定义侧：收集多余的位置参数和关键字参数"""
    print("① 收集参数（定义侧）")

    def show(*args, **kwargs):
        print(f"  args   = {args}")    # tuple
        print(f"  kwargs = {kwargs}")  # dict

    show(1, 2, 3, a=4, b=5)
    # args   = (1, 2, 3)
    # kwargs = {'a': 4, 'b': 5}

    # 只收集部分
    def greet(name, *titles, **options):
        print(f"  name={name!r}, titles={titles}, options={options}")

    greet("Alice", "Dr", "Prof", lang="zh", formal=True)
    # name='Alice', titles=('Dr', 'Prof'), options={'lang': 'zh', 'formal': True}

    # 典型场景：透传所有参数
    def wrapper(*args, **kwargs):
        print(f"  wrapper 拦截: args={args}, kwargs={kwargs}")
        return show(*args, **kwargs)   # 原封不动传给下一层

    wrapper(10, 20, x=30)


# ---------------------------------------------------------------------------
# ② 函数调用：* / ** 解包参数
# ---------------------------------------------------------------------------

def demo02_unpack_call():
    """② 调用侧：把序列/字典展开为独立参数"""
    print("\n② 解包参数（调用侧）")

    def add(x, y, z):
        return x + y + z

    nums = [1, 2, 3]
    print(f"  add(*[1,2,3])           = {add(*nums)}")      # 等价 add(1,2,3)

    info = {"x": 10, "y": 20, "z": 30}
    print(f"  add(**{{x:10,y:20,z:30}}) = {add(**info)}")   # 等价 add(x=10,y=20,z=30)

    # 混合使用
    def func(a, b, c, d):
        return a, b, c, d

    result = func(1, *[2, 3], **{"d": 4})
    print(f"  func(1, *[2,3], **{{d:4}}) = {result}")

    # 解包到 print（常用技巧）
    rows = [(1, "Alice"), (2, "Bob"), (3, "Carol")]
    for row in rows:
        print(f"  id={row[0]}, name={row[1]}")

    # 用 * 解包更简洁
    def show_row(id, name):
        print(f"  id={id}, name={name}")

    for row in rows:
        show_row(*row)


# ---------------------------------------------------------------------------
# ③ 赋值解包：*rest 捕获剩余元素
# ---------------------------------------------------------------------------

def demo03_unpack_assign():
    """③ 赋值侧：* 捕获剩余元素，结果是 list"""
    print("\n③ 赋值解包")

    seq = [1, 2, 3, 4, 5]

    first, *rest = seq
    print(f"  first={first}, rest={rest}")          # 1, [2,3,4,5]

    *init, last = seq
    print(f"  init={init}, last={last}")            # [1,2,3,4], 5

    a, *mid, b = seq
    print(f"  a={a}, mid={mid}, b={b}")             # 1, [2,3,4], 5

    # 忽略中间段
    head, *_, tail = "ABCDE"
    print(f"  head={head!r}, tail={tail!r}")        # 'A', 'E'

    # 嵌套解包
    (x, y), *others = (1, 2), 3, 4
    print(f"  x={x}, y={y}, others={others}")       # 1, 2, [3, 4]

    # 交换变量（不需要临时变量）
    p, q = 10, 20
    p, q = q, p
    print(f"  swap: p={p}, q={q}")                  # 20, 10


# ---------------------------------------------------------------------------
# ④ 字面量合并：[*a, *b] / {**d1, **d2}
# ---------------------------------------------------------------------------

def demo04_merge():
    """④ 在字面量中用 * / ** 合并序列和字典"""
    print("\n④ 合并序列 / 字典")

    # 合并列表（Python 3.5+）
    a = [1, 2, 3]
    b = [4, 5, 6]
    merged_list = [*a, 0, *b]
    print(f"  [*a, 0, *b]    = {merged_list}")      # [1,2,3,0,4,5,6]

    # 合并元组
    merged_tuple = (*a, *b)
    print(f"  (*a, *b)       = {merged_tuple}")     # (1,2,3,4,5,6)

    # 合并集合
    s1, s2 = {1, 2, 3}, {3, 4, 5}
    merged_set = {*s1, *s2}
    print(f"  {{*s1, *s2}}     = {merged_set}")      # {1,2,3,4,5}

    # 合并字典（后者覆盖前者）
    d1 = {"x": 1, "y": 2}
    d2 = {"y": 99, "z": 3}
    merged_dict = {**d1, **d2}
    print(f"  {{**d1, **d2}}   = {merged_dict}")     # {'x':1,'y':99,'z':3}

    # 实用：默认配置 + 用户配置覆盖
    defaults = {"timeout": 30, "retry": 3, "verbose": False}
    user_cfg = {"timeout": 60, "verbose": True}
    config = {**defaults, **user_cfg}
    print(f"  合并配置:       {config}")


# ---------------------------------------------------------------------------
# ⑤ 仅限关键字参数（* 作分隔符）
# ---------------------------------------------------------------------------

def demo05_keyword_only():
    """⑤ * 后面的参数必须用关键字传入"""
    print("\n⑤ 仅限关键字参数")

    # * 单独出现：后面的参数只能用关键字传
    def create_user(name, age, *, role="user", active=True):
        return {"name": name, "age": age, "role": role, "active": active}

    u1 = create_user("Alice", 30)
    u2 = create_user("Bob", 25, role="admin")
    # create_user("Carol", 20, "admin")  # TypeError：role 不能按位置传
    print(f"  u1 = {u1}")
    print(f"  u2 = {u2}")

    # *args + 关键字参数：既收集位置参数，又强制后续参数用关键字
    def log(*messages, level="INFO", sep="\n"):
        header = f"[{level}]"
        print(header + " " + sep.join(messages))

    log("启动服务", "监听端口 8080")
    log("权限不足", "访问被拒绝", level="WARN", sep=" | ")


# ---------------------------------------------------------------------------
# ⑥ 仅限位置参数（/ 作分隔符，Python 3.8+）
# ---------------------------------------------------------------------------

def demo06_positional_only():
    """⑥ / 前面的参数不能用关键字传入"""
    print("\n⑥ 仅限位置参数（Python 3.8+）")

    # / 前的参数只能按位置传（内部名称对外不可见）
    def div(a, b, /):
        return a / b

    print(f"  div(10, 2)        = {div(10, 2)}")     # OK
    # div(a=10, b=2)  # TypeError

    # 组合：/ 前仅限位置，/ 后普通，* 后仅限关键字
    def full_sig(pos_only, /, normal, *, kw_only):
        return pos_only, normal, kw_only

    result = full_sig(1, 2, kw_only=3)
    print(f"  full_sig(1, 2, kw_only=3) = {result}")

    result2 = full_sig(1, normal=2, kw_only=3)
    print(f"  full_sig(1, normal=2, kw_only=3) = {result2}")

    # 实用场景：避免参数名与 **kwargs 的键冲突
    def update(obj, /, **fields):
        for k, v in fields.items():
            setattr(obj, k, v)
        return obj

    class Point:
        def __init__(self, x, y):
            self.x, self.y = x, y
        def __repr__(self):
            return f"Point({self.x}, {self.y})"

    p = Point(1, 2)
    update(p, x=10, y=20)   # obj 是位置参数，不会与 fields 冲突
    print(f"  update Point: {p}")


if __name__ == "__main__":
    demo01_collect()
    demo02_unpack_call()
    demo03_unpack_assign()
    demo04_merge()
    demo05_keyword_only()
    demo06_positional_only()
