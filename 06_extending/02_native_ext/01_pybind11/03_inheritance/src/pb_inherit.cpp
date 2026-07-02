#include <pybind11/pybind11.h>
#include <string>
#include <vector>
#include <memory>
namespace py = pybind11;

// ── 抽象基类 ────────────────────────────────────────────────────
class Animal {
public:
    explicit Animal(std::string name) : name_(std::move(name)) {}
    virtual ~Animal() = default;

    virtual std::string speak() const = 0;   // 纯虚：子类必须实现
    virtual std::string describe() const {   // 虚：子类可选覆盖
        return name_ + " 说：\"" + speak() + "\"";
    }

    const std::string& name() const { return name_; }

protected:
    std::string name_;
};

// ── Trampoline 类 ─────────────────────────────────────────────
// 作用：桥接 C++ 虚函数调用与 Python 侧覆盖。
// 规则：每个虚函数都要用对应宏转发到 Python；trampoline 必须继承 Animal。
class PyAnimal : public Animal {
public:
    using Animal::Animal;  // 继承构造函数

    std::string speak() const override {
        // PYBIND11_OVERRIDE_PURE(返回类型, C++基类, 方法名, 参数...)
        // 若 Python 没有实现此方法则抛 NotImplementedError
        PYBIND11_OVERRIDE_PURE(std::string, Animal, speak);
    }

    std::string describe() const override {
        // PYBIND11_OVERRIDE(返回类型, C++基类, 方法名, 参数...)
        // 若 Python 没有覆盖 describe，则调用 C++ 基类实现
        PYBIND11_OVERRIDE(std::string, Animal, describe);
    }
};

// ── 具体 C++ 子类（不需要 trampoline） ─────────────────────────
class Dog : public Animal {
public:
    using Animal::Animal;
    std::string speak() const override { return "汪！"; }
};

class Cat : public Animal {
public:
    Cat(std::string name, bool indoor)
        : Animal(std::move(name)), indoor_(indoor) {}
    std::string speak() const override { return "喵～"; }
    bool is_indoor() const { return indoor_; }
private:
    bool indoor_;
};

// ── 多态函数：接收基类引用，可传入任意子类 ────────────────────
std::string make_speak(const Animal& a)  { return a.describe(); }
std::string make_speak2(Animal& a)       { return a.describe(); }

// ── keep_alive 示例：Shelter 持有 Animal* ─────────────────────
class Shelter {
public:
    void admit(Animal* a) { animals_.push_back(a); }
    size_t count() const  { return animals_.size(); }
    std::string roll_call() const {
        std::string s;
        for (auto* a : animals_) s += a->name() + " ";
        return s;
    }
private:
    std::vector<Animal*> animals_;  // 不拥有（raw ptr）
};

PYBIND11_MODULE(pb_inherit, m) {
    // ① 绑定基类：第二个模板参数 PyAnimal 是 trampoline
    //   若省略 trampoline，Python 子类不能覆盖虚函数
    py::class_<Animal, PyAnimal>(m, "Animal")
        .def(py::init<std::string>(), py::arg("name"))
        .def("speak",    &Animal::speak)
        .def("describe", &Animal::describe)
        .def_property_readonly("name", &Animal::name);

    // ② Dog 继承 Animal：py::class_<Dog, Animal>
    py::class_<Dog, Animal>(m, "Dog")
        .def(py::init<std::string>(), py::arg("name"))
        .def("speak", &Dog::speak);

    // ② Cat：额外携带 is_indoor 属性
    py::class_<Cat, Animal>(m, "Cat")
        .def(py::init<std::string, bool>(),
             py::arg("name"), py::arg("indoor") = true)
        .def("speak", &Cat::speak)
        .def_property_readonly("is_indoor", &Cat::is_indoor);

    // ④ 多态函数
    m.def("make_speak",  &make_speak,  py::arg("animal"));
    m.def("make_speak2", &make_speak2, py::arg("animal"));

    // ⑤ Shelter：keep_alive<1, 2> 确保 shelter(arg1) 存活期间 animal(arg2) 不被 GC
    py::class_<Shelter>(m, "Shelter")
        .def(py::init<>())
        .def("admit", &Shelter::admit, py::arg("animal"),
             py::keep_alive<1, 2>(),   // 1=self(Shelter), 2=animal 参数
             "收留动物（Shelter 存活则 animal 不被 GC）")
        .def("count",     &Shelter::count)
        .def("roll_call", &Shelter::roll_call);
}
