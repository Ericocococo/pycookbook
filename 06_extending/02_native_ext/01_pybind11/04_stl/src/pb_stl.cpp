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
