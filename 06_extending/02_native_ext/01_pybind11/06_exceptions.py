"""pybind11 —— 异常互转

三方库。C++17 + Python 3.12。
安装: pip install pybind11   编译器: MSVC / GCC / Clang
运行: python 06_exceptions.py

演示：
  ① C++ 标准异常自动映射到 Python 异常（pybind11 内置表）
  ② 自定义 C++ 异常注册：py::register_exception<> 映射到 Python RuntimeError 子类
  ③ 自定义异常继承层次：register_exception_translator
  ④ py::error_already_set：C++ 捕获 Python 抛出的异常
  ⑤ 从 C++ 主动抛出 Python 内置异常（pybind11 便捷 API）
"""

CPP = r"""
#include <pybind11/pybind11.h>
#include <stdexcept>
#include <string>
#include <vector>
namespace py = pybind11;

// ── 标准异常（自动映射） ─────────────────────────────────────
// pybind11 内置表（C++ -> Python）：
//   std::exception       -> Exception
//   std::bad_alloc       -> MemoryError
//   std::domain_error    -> ValueError
//   std::invalid_argument-> ValueError
//   std::length_error    -> ValueError
//   std::out_of_range    -> IndexError
//   std::range_error     -> ValueError
//   std::overflow_error  -> OverflowError
//   std::runtime_error   -> RuntimeError
void throw_std(const std::string& kind) {
    if (kind == "domain")    throw std::domain_error("域错误示例");
    if (kind == "invalid")   throw std::invalid_argument("无效参数示例");
    if (kind == "range")     throw std::out_of_range("越界示例");
    if (kind == "runtime")   throw std::runtime_error("运行时错误示例");
    if (kind == "overflow")  throw std::overflow_error("溢出示例");
    throw std::logic_error("未知 kind: " + kind);
}

// ② 自定义 C++ 异常
class DatabaseError : public std::exception {
public:
    explicit DatabaseError(std::string msg, int code = -1)
        : msg_(std::move(msg)), code_(code) {}
    const char* what() const noexcept override { return msg_.c_str(); }
    int code() const { return code_; }
private:
    std::string msg_;
    int code_;
};

class ConnectionError : public DatabaseError {
public:
    using DatabaseError::DatabaseError;
};

void db_query(const std::string& sql) {
    if (sql.empty())          throw ConnectionError("数据库未连接", 1001);
    if (sql == "bad")         throw DatabaseError("SQL 语法错误", 1002);
    // 正常执行
}

// ④ C++ 捕获 Python 异常（error_already_set）
void call_py_func(py::function f, py::object arg) {
    try {
        f(arg);
    } catch (py::error_already_set& e) {
        // error_already_set：Python 解释器里有一个活跃的异常
        py::print("C++ 捕获到 Python 异常:", e.what());
        e.restore();   // 把异常状态还给 Python 解释器
        throw;         // 重新抛出，让 pybind11 把它传回 Python 调用方
    }
}

// ⑤ 从 C++ 主动抛出 Python 内置异常
void raise_python_exc(const std::string& kind) {
    if (kind == "ValueError")    throw py::value_error("来自 C++ 的 ValueError");
    if (kind == "KeyError")      throw py::key_error("来自 C++ 的 KeyError");
    if (kind == "TypeError")     throw py::type_error("来自 C++ 的 TypeError");
    if (kind == "IndexError")    throw py::index_error("来自 C++ 的 IndexError");
    if (kind == "StopIteration") throw py::stop_iteration();
    throw py::attribute_error("来自 C++ 的 AttributeError");
}

PYBIND11_MODULE(pb_except, m) {
    // ② 注册 DatabaseError：映射为 Python RuntimeError 的子类
    //   第三个参数是 Python 基类（这里是 RuntimeError）
    auto db_err = py::register_exception<DatabaseError>(m, "DatabaseError");

    // ③ ConnectionError 继承 DatabaseError（Python 侧同样继承）
    py::register_exception<ConnectionError>(m, "ConnectionError", db_err);

    m.def("throw_std",       &throw_std,       py::arg("kind"));
    m.def("db_query",        &db_query,        py::arg("sql"));
    m.def("call_py_func",    &call_py_func,    py::arg("f"), py::arg("arg"));
    m.def("raise_python_exc",&raise_python_exc, py::arg("kind"));
}
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _build import build_and_import  # noqa: E402

_m = None


def demo01_std_exceptions():
    """① 标准异常自动映射"""
    mapping = {
        "domain":   ValueError,
        "invalid":  ValueError,
        "range":    IndexError,
        "runtime":  RuntimeError,
        "overflow": OverflowError,
    }
    print("① 标准异常映射：")
    for kind, expected in mapping.items():
        try:
            _m.throw_std(kind)
        except expected as e:
            print(f"  {kind:10s} -> {type(e).__name__}: {e}")


def demo02_custom_exception():
    """② 自定义异常"""
    print("② 自定义异常：")
    for sql in ["", "bad", "SELECT 1"]:
        label = repr(sql)
        try:
            _m.db_query(sql)
            print(f"  db_query({label:15}) -> OK")
        except _m.ConnectionError as e:
            print(f"  db_query({label:15}) -> ConnectionError: {e}")
        except _m.DatabaseError as e:
            print(f"  db_query({label:15}) -> DatabaseError: {e}")


def demo03_exception_hierarchy():
    """③ 异常继承关系"""
    try:
        _m.db_query("")
    except _m.DatabaseError as e:
        # ConnectionError 是 DatabaseError 的子类，catch 到了
        print("③ 用 DatabaseError 捕获 ConnectionError:", type(e).__name__)
    print("  issubclass:", issubclass(_m.ConnectionError, _m.DatabaseError))


def demo04_error_already_set():
    """④ error_already_set：C++ 捕获 Python 异常"""
    def bad_func(x):
        if x > 0:
            raise ValueError(f"x={x} 不合法（Python 抛出）")

    print("④ 传入会抛异常的 Python 函数：")
    try:
        _m.call_py_func(bad_func, 5)
    except ValueError as e:
        print("  最终 Python 侧捕获到:", e)


def demo05_raise_python():
    """⑤ 从 C++ 抛出 Python 内置异常"""
    kinds = ["ValueError", "KeyError", "TypeError", "IndexError"]
    print("⑤ 从 C++ 主动抛出内置异常：")
    for k in kinds:
        try:
            _m.raise_python_exc(k)
        except Exception as e:
            print(f"  {k}: {type(e).__name__}: {e}")


if __name__ == "__main__":
    _m = build_and_import("pb_except", CPP)
    if _m is None:
        sys.exit(0)
    demo01_std_exceptions()
    print()
    demo02_custom_exception()
    print()
    demo03_exception_hierarchy()
    print()
    demo04_error_already_set()
    print()
    demo05_raise_python()
