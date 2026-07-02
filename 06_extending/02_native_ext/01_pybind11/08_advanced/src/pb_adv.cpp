#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <memory>
#include <string>
#include <vector>
#include <cstring>
namespace py = pybind11;

// ── ① 枚举 ───────────────────────────────────────────────────
enum class Color { RED = 0, GREEN = 1, BLUE = 2 };

// 算术枚举（py::arithmetic<>）：支持位运算，常用于 flags
enum class Flags : uint32_t {
    NONE  = 0,
    READ  = 1 << 0,
    WRITE = 1 << 1,
    EXEC  = 1 << 2,
};

// ── ② shared_ptr ─────────────────────────────────────────────
class Resource {
public:
    explicit Resource(std::string name) : name_(std::move(name)) {
        py::print("Resource 创建:", name_);
    }
    ~Resource() { py::print("Resource 销毁:", name_); }

    const std::string& name() const { return name_; }
    std::string info() const { return "Resource(" + name_ + ")"; }

    // 工厂：返回 shared_ptr（Python 侧得到同一引用计数对象）
    static std::shared_ptr<Resource> create(const std::string& n) {
        return std::make_shared<Resource>(n);
    }
private:
    std::string name_;
};

// ── ③ GIL 管理 ───────────────────────────────────────────────
// 释放 GIL 让其他 Python 线程运行；重新获取后才能调用 Python API
std::vector<double> compute_heavy(int n) {
    std::vector<double> result;
    result.reserve(n);
    {
        py::gil_scoped_release release;  // ← 释放 GIL
        // 纯 C++ 计算，无需 GIL
        for (int i = 0; i < n; ++i)
            result.push_back(i * 3.14159265358979);
    }  // ← GIL 自动归还（RAII）
    return result;
}

// 在无 GIL 的线程里重新获取 GIL 后调用 Python
void threaded_callback(py::function cb, int value) {
    // 假设这个函数在非 Python 线程中被调用（如 C++ 工作线程）
    py::gil_scoped_acquire acquire;  // ← 先获取 GIL 才能调 Python
    cb(value);
}

// ── ④ capsule ─────────────────────────────────────────────────
// capsule：将 C++ 资源（裸指针/非 pybind11 对象）包裹成 Python 对象
// 常用于：跨模块共享 C++ 指针（如 NumPy 的 __array_struct__）
py::capsule make_int_array(int size) {
    int* arr = new int[size];
    for (int i = 0; i < size; ++i) arr[i] = i * i;  // 0,1,4,9,...
    // 第三个参数是析构函数（void(*)(void*)），capsule 被 GC 时调用
    return py::capsule(arr, "int_array", [](void* p) {
        delete[] static_cast<int*>(p);
    });
}

int read_capsule(py::capsule cap, int idx) {
    // 用 capsule 的名称验证类型
    if (std::string(cap.name()) != "int_array")
        throw std::invalid_argument("非 int_array capsule");
    return cap.get_pointer<int>()[idx];
}

// ── ⑤ bytes / memoryview ─────────────────────────────────────
py::bytes encode_ints(const std::vector<int>& v) {
    // 把 int[] 序列化为原始字节（小端 4 字节/个）
    std::vector<char> buf(v.size() * sizeof(int));
    std::memcpy(buf.data(), v.data(), buf.size());
    return py::bytes(buf.data(), buf.size());
}

std::vector<int> decode_ints(py::bytes data) {
    py::buffer_info info = py::memoryview::from_memory(
        const_cast<char*>(PyBytes_AS_STRING(data.ptr())),
        static_cast<py::ssize_t>(PyBytes_GET_SIZE(data.ptr()))
    ).request();
    auto* ptr = static_cast<int*>(info.ptr);
    size_t n = info.size / sizeof(int);
    return {ptr, ptr + n};
}

PYBIND11_MODULE(pb_adv, m) {
    // ① 普通枚举
    py::enum_<Color>(m, "Color")
        .value("RED",   Color::RED)
        .value("GREEN", Color::GREEN)
        .value("BLUE",  Color::BLUE)
        .export_values();   // 把 RED/GREEN/BLUE 也导出到模块作用域（可选）

    // ① 算术枚举（py::arithmetic）：支持 | & ^ 运算
    py::enum_<Flags>(m, "Flags", py::arithmetic())
        .value("NONE",  Flags::NONE)
        .value("READ",  Flags::READ)
        .value("WRITE", Flags::WRITE)
        .value("EXEC",  Flags::EXEC);

    // ② shared_ptr：py::class_<T, shared_ptr<T>>
    py::class_<Resource, std::shared_ptr<Resource>>(m, "Resource")
        .def(py::init<std::string>(), py::arg("name"))
        .def_property_readonly("name", &Resource::name)
        .def("info", &Resource::info)
        .def_static("create", &Resource::create, py::arg("name"),
                    "工厂方法，返回 shared_ptr");

    // ③ GIL
    m.def("compute_heavy",    &compute_heavy,    py::arg("n"),
          "释放 GIL 进行纯 C++ 计算，其他 Python 线程可在此期间运行");
    m.def("threaded_callback",&threaded_callback, py::arg("cb"), py::arg("value"),
          "演示在获取 GIL 后调用 Python 函数");

    // ④ capsule
    m.def("make_int_array", &make_int_array, py::arg("size"));
    m.def("read_capsule",   &read_capsule,   py::arg("cap"), py::arg("idx"));

    // ⑤ bytes
    m.def("encode_ints", &encode_ints, py::arg("v"));
    m.def("decode_ints", &decode_ints, py::arg("data"));

    // ⑥ 模块初始化时可以执行任意 Python 操作（通过 pybind11 API）
    m.attr("BUILD_INFO") = py::dict(
        py::arg("pybind11") = py::module_::import("pybind11").attr("__version__"),
        py::arg("platform") = py::module_::import("sys").attr("platform")
    );
}
