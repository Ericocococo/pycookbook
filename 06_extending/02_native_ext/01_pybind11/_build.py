"""内部编译工具 —— 供各配方文件 import，不直接运行。"""
import importlib
import subprocess
import sys
from pathlib import Path

_DATA = Path(__file__).parent / "data"


def build_and_import(module_name: str, cpp_src: str):
    """
    将 C++ 源码写入 data/，编译为扩展模块，注入 sys.path 后返回模块对象。
    编译工具缺失时返回 None 并打印提示，不中断程序。
    """
    try:
        import pybind11  # noqa: F401
    except ImportError:
        print("[跳过] 需要安装 pybind11: pip install pybind11")
        return None

    _DATA.mkdir(exist_ok=True)
    cpp_file = _DATA / f"{module_name}.cpp"
    cpp_file.write_text(cpp_src, encoding="utf-8")

    # 已有产物且比源码新 → 直接 import
    existing = (
        list(_DATA.glob(f"{module_name}*.pyd"))
        + list(_DATA.glob(f"{module_name}*.so"))
    )
    if existing and existing[0].stat().st_mtime >= cpp_file.stat().st_mtime:
        _inject(existing[0].parent)
        sys.modules.pop(module_name, None)
        try:
            return importlib.import_module(module_name)
        except ImportError:
            pass  # 产物失效，重新编译

    print(f"[编译] {module_name}.cpp ...")
    if not _compile(module_name, cpp_file):
        return None

    _inject(_DATA)
    sys.modules.pop(module_name, None)
    return importlib.import_module(module_name)


def _inject(path: Path) -> None:
    """将 path 注入 sys.path（避免重复）。"""
    s = str(path)
    if s not in sys.path:
        sys.path.insert(0, s)


def _compile(module_name: str, cpp_file: Path) -> bool:
    import pybind11

    extra = (
        ["/std:c++17", "/EHsc"]
        if sys.platform == "win32"
        else ["-std=c++17", "-fvisibility=hidden"]
    )
    setup_src = (
        "from setuptools import setup, Extension\n"
        "import pybind11\n"
        f"e = Extension(\n"
        f"    '{module_name}',\n"
        f"    sources=[r'{cpp_file}'],\n"
        f"    include_dirs=[pybind11.get_include()],\n"
        f"    language='c++',\n"
        f"    extra_compile_args={extra!r},\n"
        f")\n"
        f"setup(name='{module_name}', ext_modules=[e])\n"
    )
    setup_py = _DATA / "_setup_tmp.py"
    setup_py.write_text(setup_src, encoding="utf-8")

    r = subprocess.run(
        [sys.executable, str(setup_py), "build_ext", "--inplace"],
        cwd=str(_DATA),
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        print(f"[编译失败] {module_name}")
        print("\n".join(r.stderr.splitlines()[-20:]))
        return False
    return True
