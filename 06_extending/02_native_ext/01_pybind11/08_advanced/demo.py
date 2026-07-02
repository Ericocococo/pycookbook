"""pybind11 —— 进阶特性

三方库。C++17 + Python 3.12。
构建: cmake --build build/  (demo.py 首次运行自动触发)
运行: python demo.py

演示：
  ① py::enum_<T>：绑定 C++ 枚举（算术枚举 / 非算术枚举）
  ② std::shared_ptr<T>：智能指针管理对象生命周期
  ③ GIL 管理：gil_scoped_release（释放）/ gil_scoped_acquire（重新获取）
  ④ py::capsule：将 C++ 裸指针包装成 Python 胶囊对象（跨模块传递）
  ⑤ py::bytes / py::memoryview：二进制数据处理
  ⑥ 模块初始化钩子与 PYBIND11_MODULE 里的任意 Python 操作
"""

import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))   # _cmake_build 在上级目录
from _cmake_build import build_and_import  # noqa: E402



_m = None


def demo01_enum():
    """① 枚举绑定"""
    c = _m.Color.RED
    print("① Color.RED:", c, type(c))
    print("  Color.GREEN.value:", _m.Color.GREEN.value)
    print("  export_values → RED 在模块作用域:", _m.RED)

    # 算术枚举支持位运算
    flags = _m.Flags.READ | _m.Flags.WRITE
    print("  READ | WRITE:", flags)
    print("  has READ:", bool(flags & _m.Flags.READ))


def demo02_shared_ptr():
    """② shared_ptr 生命周期"""
    print("② shared_ptr：")
    r1 = _m.Resource.create("资源A")
    r2 = r1                    # 同一 shared_ptr，引用计数 +1
    print("  r1.info():", r1.info())
    print("  r1 is r2:", r1 is r2)  # True（同一 Python 对象）
    # 出函数后 r1/r2 都释放 → shared_ptr 计数归零 → C++ 析构


def demo03_gil():
    """③ GIL 释放与恢复"""
    result = _m.compute_heavy(5)
    print("③ compute_heavy(5):", result)

    log = []
    _m.threaded_callback(lambda v: log.append(v), 42)
    print("  threaded_callback result:", log)


def demo04_capsule():
    """④ py::capsule"""
    cap = _m.make_int_array(5)
    print("④ capsule:", cap, type(cap))
    for i in range(5):
        print(f"  [{i}] = {_m.read_capsule(cap, i)}")


def demo05_bytes():
    """⑤ bytes / decode"""
    data = _m.encode_ints([1, 2, 3, 100])
    print("⑤ encode_ints([1,2,3,100]):", data[:16], "len=", len(data))
    decoded = _m.decode_ints(data)
    print("  decode_ints:", decoded)


def demo06_build_info():
    """⑥ 模块初始化期间设置的属性"""
    print("⑥ BUILD_INFO:", dict(_m.BUILD_INFO))


if __name__ == "__main__":
    _m = build_and_import(HERE, "pb_adv")
    if _m is None:
        sys.exit(0)
    demo01_enum()
    print()
    demo02_shared_ptr()
    print()
    demo03_gil()
    print()
    demo04_capsule()
    print()
    demo05_bytes()
    print()
    demo06_build_info()
