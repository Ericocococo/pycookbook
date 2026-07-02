"""pybind11 —— 回调函数与 std::function

三方库。C++17 + Python 3.12。
安装: pip install pybind11   编译器: MSVC / GCC / Clang
运行: python 07_callbacks.py

演示：
  ① std::function<R(Args)> 接收 Python 可调用对象（需 #include <pybind11/functional.h>）
  ② py::function：直接持有 Python callable，延迟调用
  ③ 存储回调：C++ 类持有 py::function，稍后触发（EventEmitter 模式）
  ④ C++ 调用 Python 函数时的 GIL 注意事项
  ⑤ 高阶函数：vec_map / vec_filter / vec_reduce
"""

CPP = r"""
#include <pybind11/pybind11.h>
#include <pybind11/functional.h>  // std::function 与 Python callable 互转
#include <pybind11/stl.h>
#include <functional>
#include <map>
#include <vector>
#include <string>
#include <stdexcept>
namespace py = pybind11;

// ① std::function 接收 Python callable
int apply_int(std::function<int(int)> f, int x) { return f(x); }
double apply_double(std::function<double(double)> f, double x) { return f(x); }

// ⑤ 高阶函数
std::vector<int> vec_map(const std::vector<int>& v,
                         std::function<int(int)> f) {
    std::vector<int> r;
    r.reserve(v.size());
    for (int x : v) r.push_back(f(x));
    return r;
}

std::vector<int> vec_filter(const std::vector<int>& v,
                             std::function<bool(int)> pred) {
    std::vector<int> r;
    for (int x : v) if (pred(x)) r.push_back(x);
    return r;
}

int vec_reduce(const std::vector<int>& v,
               std::function<int(int, int)> f, int init) {
    int acc = init;
    for (int x : v) acc = f(acc, x);
    return acc;
}

// ② py::function：直接持有 Python callable，可延迟调用
void call_twice(py::function f, py::object arg) {
    f(arg);
    f(arg);
}

// 调用并捕获 Python 异常
py::object safe_call(py::function f, py::object arg) {
    try {
        return f(arg);
    } catch (py::error_already_set& e) {
        py::print("安全调用捕获异常:", e.what());
        e.restore();
        throw;
    }
}

// ③ EventEmitter：C++ 对象持有多个 Python 回调
class EventEmitter {
public:
    // 注册回调（允许同一事件多个）
    void on(const std::string& event, py::function cb) {
        handlers_[event].push_back(std::move(cb));
    }

    // 触发事件，把 data 传给所有回调
    void emit(const std::string& event, py::object data = py::none()) {
        auto it = handlers_.find(event);
        if (it == handlers_.end()) return;
        for (auto& cb : it->second)
            cb(data);
    }

    void off(const std::string& event) { handlers_.erase(event); }
    size_t listener_count(const std::string& event) const {
        auto it = handlers_.find(event);
        return it == handlers_.end() ? 0 : it->second.size();
    }

private:
    std::map<std::string, std::vector<py::function>> handlers_;
};

PYBIND11_MODULE(pb_cb, m) {
    m.def("apply_int",    &apply_int,    py::arg("f"), py::arg("x"));
    m.def("apply_double", &apply_double, py::arg("f"), py::arg("x"));
    m.def("call_twice",   &call_twice,   py::arg("f"), py::arg("arg"));
    m.def("safe_call",    &safe_call,    py::arg("f"), py::arg("arg"));
    m.def("vec_map",      &vec_map,      py::arg("v"), py::arg("f"));
    m.def("vec_filter",   &vec_filter,   py::arg("v"), py::arg("pred"));
    m.def("vec_reduce",   &vec_reduce,   py::arg("v"), py::arg("f"), py::arg("init"));

    py::class_<EventEmitter>(m, "EventEmitter",
        "简易事件发射器：支持多事件、多回调")
        .def(py::init<>())
        .def("on",             &EventEmitter::on,
             py::arg("event"), py::arg("callback"),
             "注册事件回调")
        .def("emit",           &EventEmitter::emit,
             py::arg("event"), py::arg("data") = py::none(),
             "触发事件")
        .def("off",            &EventEmitter::off,   py::arg("event"))
        .def("listener_count", &EventEmitter::listener_count, py::arg("event"));
}
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _build import build_and_import  # noqa: E402

_m = None


def demo01_std_function():
    """① std::function 接收 Python callable"""
    result = _m.apply_int(lambda x: x * x, 7)
    print("① apply_int(x^2, 7):", result, type(result))

    result2 = _m.apply_double(lambda x: x ** 0.5, 2.0)
    print("  apply_double(sqrt, 2.0):", round(result2, 6))

    # 传普通函数也可以
    import math
    print("  apply_double(math.sin, pi/2):", round(_m.apply_double(math.sin, 3.14159 / 2), 4))


def demo02_py_function():
    """② py::function 直接持有"""
    log = []
    _m.call_twice(lambda x: log.append(x), "hello")
    print("② call_twice 结果:", log)


def demo03_higher_order():
    """③ 高阶函数：map / filter / reduce"""
    nums = list(range(1, 11))
    mapped  = _m.vec_map(nums, lambda x: x * x)
    filtered = _m.vec_filter(nums, lambda x: x % 2 == 0)
    total    = _m.vec_reduce(nums, lambda a, b: a + b, 0)
    print("③ vec_map([1..10], x^2):", mapped)
    print("  vec_filter([1..10], even):", filtered)
    print("  vec_reduce([1..10], +, 0):", total)


def demo04_event_emitter():
    """④ EventEmitter：C++ 持有 Python 回调"""
    ee = _m.EventEmitter()
    log = []

    ee.on("data", lambda d: log.append(f"handler1: {d}"))
    ee.on("data", lambda d: log.append(f"handler2: {d!r}"))
    ee.on("close", lambda _: log.append("closed"))

    print("④ listener_count('data'):", ee.listener_count("data"))
    ee.emit("data", "hello")
    ee.emit("data", 42)
    ee.emit("close")
    ee.emit("unknown")   # 没有注册，静默忽略

    for entry in log:
        print(" ", entry)


def demo05_error_in_callback():
    """⑤ 回调抛异常的处理"""
    def bad_callback(x):
        if isinstance(x, int) and x < 0:
            raise ValueError(f"不接受负数: {x}")
        return x

    print("⑤ safe_call(正常):", _m.safe_call(bad_callback, 5))
    try:
        _m.safe_call(bad_callback, -1)
    except ValueError as e:
        print("  safe_call(负数) 捕获:", e)


if __name__ == "__main__":
    _m = build_and_import("pb_cb", CPP)
    if _m is None:
        sys.exit(0)
    demo01_std_function()
    print()
    demo02_py_function()
    print()
    demo03_higher_order()
    print()
    demo04_event_emitter()
    print()
    demo05_error_in_callback()
