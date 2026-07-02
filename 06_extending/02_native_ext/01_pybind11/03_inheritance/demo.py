"""pybind11 —— 继承与虚函数

三方库。C++17 + Python 3.12。
构建: cmake --build build/  (demo.py 首次运行自动触发)
运行: python demo.py

演示：
  ① py::class_<Derived, Base> 普通继承（C++ 具体子类）
  ② Trampoline 类：让 Python 子类可覆盖 C++ 虚函数
  ③ PYBIND11_OVERRIDE_PURE（纯虚）/ PYBIND11_OVERRIDE（可选覆盖）
  ④ 多态调用：C++ 函数接收基类引用，Python 子类也能传入
  ⑤ py::keep_alive<>：控制对象生命周期依赖
"""

import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))   # _cmake_build 在上级目录
from _cmake_build import build_and_import  # noqa: E402



_m = None


def demo01_concrete():
    """① C++ 具体子类"""
    dog = _m.Dog("旺财")
    cat = _m.Cat("咪咪", indoor=True)
    print("① Dog.speak():", dog.speak())
    print("  Cat.speak():", cat.speak())
    print("  Dog.describe():", dog.describe())
    print("  Cat.is_indoor:", cat.is_indoor)
    # isinstance 也能识别继承关系
    print("  isinstance(dog, Animal):", isinstance(dog, _m.Animal))


def demo02_python_subclass():
    """② Python 子类覆盖虚函数"""
    class Parrot(_m.Animal):
        def speak(self):
            return "你好！你好！"
        def describe(self):           # 可选：覆盖 describe
            return f"鹦鹉{self.name}在说话"

    bird = Parrot("小绿")
    print("② Parrot.speak():", bird.speak())
    print("  Parrot.describe():", bird.describe())

    # 只覆盖 speak，describe 回退到 C++ 实现
    class Crow(_m.Animal):
        def speak(self):
            return "呱！"

    crow = Crow("乌鸦")
    print("  Crow.speak():", crow.speak())
    print("  Crow.describe():", crow.describe())  # C++ 的 describe


def demo03_polymorphism():
    """③ 多态调用"""
    animals = [_m.Dog("旺财"), _m.Cat("咪咪"), ]

    class Fish(_m.Animal):
        def speak(self): return "...（沉默）"

    animals.append(Fish("金鱼"))
    print("③ 多态 make_speak:")
    for a in animals:
        print(" ", _m.make_speak(a))


def demo04_keep_alive():
    """④ keep_alive：保持 animal 存活"""
    shelter = _m.Shelter()
    dog = _m.Dog("阿黄")
    cat = _m.Cat("小白")
    shelter.admit(dog)
    shelter.admit(cat)
    print("④ shelter.count():", shelter.count())
    print("  roll_call:", shelter.roll_call())


if __name__ == "__main__":
    _m = build_and_import(HERE, "pb_inherit")
    if _m is None:
        sys.exit(0)
    demo01_concrete()
    print()
    demo02_python_subclass()
    print()
    demo03_polymorphism()
    print()
    demo04_keep_alive()
