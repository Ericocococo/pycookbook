"""pybind11 —— STL 容器类型自动转换

三方库。C++17 + Python 3.12。
构建: cmake --build build/  (demo.py 首次运行自动触发)
运行: python demo.py

演示：
  ① #include <pybind11/stl.h>：vector / map / set 自动 ↔ list/dict/set（拷贝语义）
  ② std::optional<T> ↔ T | None
  ③ std::variant<T...> ↔ Python 对应类型（int / float / str）
  ④ std::pair / std::tuple ↔ Python tuple
  ⑤ py::bind_vector / py::bind_map：暴露容器本身（引用语义，无拷贝）
"""

import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))   # _cmake_build 在上级目录
from _cmake_build import build_and_import  # noqa: E402



_m = None


def demo01_containers():
    """① vector / map / set 自动转换"""
    rng = _m.make_range(5)
    print("① make_range(5):", rng, type(rng))            # Python list

    total = _m.sum_vec([1.5, 2.5, 3.0])
    print("  sum_vec([1.5,2.5,3.0]):", total)

    wc = _m.word_count(["apple", "banana", "apple", "cherry", "banana", "apple"])
    print("  word_count:", wc, type(wc))                  # Python dict

    unique = _m.dedupe([3, 1, 4, 1, 5, 9, 2, 6, 5])
    print("  dedupe:", unique, type(unique))               # Python set


def demo02_optional():
    """② optional → None | T"""
    print("② find_index([10,20,30], 20):", _m.find_index([10, 20, 30], 20))
    print("  find_index([10,20,30], 99):", _m.find_index([10, 20, 30], 99))   # None
    print("  safe_log(2.718):", round(_m.safe_log(2.718), 4))
    print("  safe_log(-1.0):", _m.safe_log(-1.0))                            # None


def demo03_variant():
    """③ variant → 对应 Python 类型"""
    cases = ["42", "3.14", "hello"]
    for s in cases:
        v = _m.parse(s)
        print(f"  parse({s!r}) -> {v!r}  ({type(v).__name__}, C++: {_m.type_of(v)})")


def demo04_pair_tuple():
    """④ pair / tuple → Python tuple"""
    mm = _m.minmax([3.0, 1.0, 4.0, 1.0, 5.9])
    print("④ minmax:", mm, type(mm))
    row = _m.make_row(7)
    print("  make_row(7):", row, type(row))
    id_, val, label = row          # 解包
    print("  解包：id=%d  val=%.2f  label=%s" % (id_, val, label))


def demo05_bind_vector():
    """⑤ bind_vector：引用语义"""
    dv = _m.DoubleVector([1.0, 2.0, 3.0])
    print("⑤ DoubleVector:", list(dv), type(dv))
    dv.append(4.0)
    dv[0] = 99.0
    print("  修改后:", list(dv))

    sm = _m.StrIntMap({"a": 1, "b": 2})
    print("  StrIntMap:", dict(sm), type(sm))
    sm["c"] = 3
    print("  添加 c 后:", dict(sm))


if __name__ == "__main__":
    _m = build_and_import(HERE, "pb_stl")
    if _m is None:
        sys.exit(0)
    demo01_containers()
    print()
    demo02_optional()
    print()
    demo03_variant()
    print()
    demo04_pair_tuple()
    print()
    demo05_bind_vector()
