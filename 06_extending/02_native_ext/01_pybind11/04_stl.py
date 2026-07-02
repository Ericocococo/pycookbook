"""pybind11 —— STL 容器类型自动转换

三方库。C++17 + Python 3.12。
安装: pip install pybind11   编译器: MSVC / GCC / Clang
运行: python 04_stl.py

演示：
  ① #include <pybind11/stl.h>：vector / map / set 自动 ↔ list/dict/set（拷贝语义）
  ② std::optional<T> ↔ T | None
  ③ std::variant<T...> ↔ Python 对应类型（int / float / str）
  ④ std::pair / std::tuple ↔ Python tuple
  ⑤ py::bind_vector / py::bind_map：暴露容器本身（引用语义，无拷贝）
"""

CPP = r"""
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>        // 自动转换（include 即生效，拷贝语义）
#include <pybind11/stl_bind.h>   // 绑定容器本身（引用语义）
#include <vector>
#include <map>
#include <set>
#include <optional>
#include <variant>
#include <tuple>
#include <string>
#include <numeric>
#include <cmath>
namespace py = pybind11;

// ① vector / map / set
std::vector<int> make_range(int n) {
    std::vector<int> v(n);
    std::iota(v.begin(), v.end(), 0);   // 0,1,2,...,n-1
    return v;
}

double sum_vec(const std::vector<double>& v) {
    double s = 0.0;
    for (double x : v) s += x;
    return s;
}

std::map<std::string, int> word_count(const std::vector<std::string>& words) {
    std::map<std::string, int> cnt;
    for (const auto& w : words) cnt[w]++;
    return cnt;
}

std::set<int> dedupe(const std::vector<int>& v) {
    return {v.begin(), v.end()};
}

// ② optional：找不到返回 None
std::optional<int> find_index(const std::vector<int>& v, int target) {
    for (int i = 0; i < static_cast<int>(v.size()); ++i)
        if (v[i] == target) return i;
    return std::nullopt;   // → Python None
}

std::optional<double> safe_log(double x) {
    if (x <= 0.0) return std::nullopt;
    return std::log(x);
}

// ③ variant：将字符串解析为 int / double / string
using Value = std::variant<int, double, std::string>;

Value parse(const std::string& s) {
    try { return std::stoi(s); }  catch (...) {}
    try { return std::stod(s); }  catch (...) {}
    return s;
}

std::string type_of(const Value& v) {
    return std::visit([](const auto& x) -> std::string {
        using T = std::decay_t<decltype(x)>;
        if constexpr (std::is_same_v<T, int>)         return "int";
        else if constexpr (std::is_same_v<T, double>) return "double";
        else                                           return "string";
    }, v);
}

// ④ pair / tuple
std::pair<double, double> minmax(const std::vector<double>& v) {
    auto [lo, hi] = std::minmax_element(v.begin(), v.end());
    return {*lo, *hi};
}

std::tuple<int, double, std::string> make_row(int id) {
    return {id, id * 3.14, "row_" + std::to_string(id)};
}

PYBIND11_MODULE(pb_stl, m) {
    // ① 自动转换（函数签名里的 STL 类型 stl.h 会自动处理）
    m.def("make_range",  &make_range,  py::arg("n"));
    m.def("sum_vec",     &sum_vec,     py::arg("v"));
    m.def("word_count",  &word_count,  py::arg("words"));
    m.def("dedupe",      &dedupe,      py::arg("v"));

    // ② optional → None | T
    m.def("find_index", &find_index, py::arg("v"), py::arg("target"));
    m.def("safe_log",   &safe_log,   py::arg("x"));

    // ③ variant
    m.def("parse",   &parse,   py::arg("s"));
    m.def("type_of", &type_of, py::arg("v"));

    // ④ pair / tuple → Python tuple（自动转换）
    m.def("minmax",   &minmax,   py::arg("v"));
    m.def("make_row", &make_row, py::arg("id"));

    // ⑤ bind_vector：暴露 std::vector<double> 为 Python 类（引用语义）
    //   优点：in-place 修改立即生效，大数组避免拷贝开销
    //   缺点：Python 代码无法用普通 list 字面量直接传入
    py::bind_vector<std::vector<double>>(m, "DoubleVector",
        "直接暴露的 std::vector<double>，修改立即反映（引用语义）");
    py::bind_map<std::map<std::string, int>>(m, "StrIntMap",
        "直接暴露的 std::map<str, int>（引用语义）");
}
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _build import build_and_import  # noqa: E402

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
    _m = build_and_import("pb_stl", CPP)
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
