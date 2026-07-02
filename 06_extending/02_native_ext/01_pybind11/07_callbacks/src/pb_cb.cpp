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
