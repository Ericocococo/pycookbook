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
