"""共享 CMake 编译辅助工具 —— 供各 demo.py import，不直接运行。

支持两套工具链，各用自己的 CMake / Ninja：
  MSVC   cl.exe + link.exe，CMake/Ninja 用 Visual Studio 自带版本
  MinGW  g++，CMake/Ninja 用 CLion 内置版本

工具链路径（与 cppcookbook 一致）：
  VS cmake  D:/Program Files/Microsoft Visual Studio/18/Community/Common7/IDE/...
  VS ninja  D:/Program Files/Microsoft Visual Studio/18/Community/Common7/IDE/...
  MSVC cl   D:/Program Files/Microsoft Visual Studio/18/Community/VC/Tools/...
  CLion cmake D:/ProgramData/JetBrains/CLion20260101/bin/cmake/...
  CLion ninja D:/ProgramData/JetBrains/CLion20260101/bin/ninja/...
  Python 3.12 D:/ProgramData/anaconda3/envs/quant312/python.exe

[configure] D:\ProgramData\JetBrains\CLion20260101\bin\cmake\win\x64\bin\cmake.exe D:\workspace\pycharm_workspace\d\pycookbook\06_extending\02_native_ext\01_pybind11\01_basic -DCMAKE_MAKE_PROGRAM=D:\ProgramData\JetBrains\CLion20260101\bin\ninja\win\x64\ninja.exe -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER=D:\ProgramData\JetBrains\CLion20260101\bin\mingw\bin\g++.exe
    [build] D:\ProgramData\JetBrains\CLion20260101\bin\cmake\win\x64\bin\cmake.exe --build .

[configure] "D:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe" D:\workspace\pycharm_workspace\d\pycookbook\06_extending\02_native_ext\01_pybind11\01_basic "-DCMAKE_MAKE_PROGRAM=D:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe" -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER=cl.exe "-DCMAKE_LINKER=D:\Program Files\Microsoft Visual Studio\18\Community\VC\Tools\MSVC\14.51.36231\bin\Hostx64\x64\link.exe"
    [build] "D:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe" --build .

"""
import importlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

# ── 公共路径 ──────────────────────────────────────────────────────────────────
PYTHON = r"D:\ProgramData\anaconda3\envs\quant312\python.exe"

# ── MSVC 工具链路径（VS 自带 CMake / Ninja）──────────────────────────────────
MSVC_CMAKE = r"D:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe"
MSVC_NINJA = r"D:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe"
VCVARS     = r"D:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvarsall.bat"
MSVC_CXX   = r"D:\Program Files\Microsoft Visual Studio\18\Community\VC\Tools\MSVC\14.51.36231\bin\Hostx64\x64\cl.exe"
MSVC_LD    = r"D:\Program Files\Microsoft Visual Studio\18\Community\VC\Tools\MSVC\14.51.36231\bin\Hostx64\x64\link.exe"

# ── MinGW 工具链路径（CLion 内置 CMake / Ninja，g++ 按候选路径检测）────────────
MINGW_CMAKE = r"D:\ProgramData\JetBrains\CLion20260101\bin\cmake\win\x64\bin\cmake.exe"
MINGW_NINJA = r"D:\ProgramData\JetBrains\CLion20260101\bin\ninja\win\x64\ninja.exe"
_MINGW_CXX_CANDIDATES = [
    r"D:\ProgramData\JetBrains\CLion20260101\bin\mingw\bin\g++.exe",  # CLion 内置
]


# ── 工具链实现 ────────────────────────────────────────────────────────────────

def _msvc_env() -> dict | None:
    """通过 vcvarsall.bat amd64 获取 MSVC 完整环境变量字典。"""
    if not Path(VCVARS).exists():
        return None
    r = subprocess.run(
        f'"{VCVARS}" amd64 && set',
        shell=True, capture_output=True, text=True,
    )
    env: dict[str, str] = {}
    for line in r.stdout.splitlines():
        if "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env if env else None


def _find_mingw_cxx() -> str | None:
    """在候选路径列表里找 g++，找不到再查 PATH。"""
    for p in _MINGW_CXX_CANDIDATES:
        if Path(p).exists():
            return p
    return shutil.which("g++")


def _msvc_available() -> bool:
    return Path(VCVARS).exists()


def _mingw_available() -> bool:
    return _find_mingw_cxx() is not None


# ── 核心构建函数 ──────────────────────────────────────────────────────────────

def build_and_import(project_dir: Path,module_name: str,toolchain: str = "auto",):
    """用 CMake + Ninja 编译 pybind11 扩展，注入 sys.path 后返回模块对象。

    project_dir : CMakeLists.txt 所在目录（各配方子文件夹）
    module_name : PYBIND11_MODULE 里声明的模块名（如 "pb_basic"）
    toolchain   : "auto"（默认，优先 MSVC）/ "msvc" / "mingw"
    返回         : 模块对象；编译失败时返回 None 并打印错误。
    """
    # 解析工具链
    tc = _resolve_toolchain(toolchain)
    if tc is None:
        print(f"  [跳过] 找不到可用工具链（toolchain={toolchain!r}）")
        return None

    build_dir = project_dir / "build"
    build_dir.mkdir(exist_ok=True)

    # 已有产物 → 直接 import
    existing = (list(build_dir.rglob(f"{module_name}*.pyd")) +
                list(build_dir.rglob(f"{module_name}*.so")))
    if existing:
        # ① 把 .pyd 所在目录加入 sys.path，import_module 才能按名称找到它
        _inject(existing[0].parent)
        # ② MinGW 编译的 .pyd 依赖 libgcc / libstdc++ 等运行时 DLL，
        #    必须把 MinGW bin 目录加入 PATH，Windows 才能在 import 时找到这些 DLL
        _inject_path(tc.get("runtime_bin"))
        # ③ 清除旧缓存：不 pop 的话 import_module 直接返回缓存，不会读取新 .pyd
        sys.modules.pop(module_name, None)
        try:
            # ④ 从磁盘加载最新的 .pyd，填入 sys.modules 并返回
            return importlib.import_module(module_name)
        except ImportError:
            pass  # 产物文件损坏或 ABI 不匹配，跌落到重新编译流程

    print(f"[CMake] 编译 {module_name} （工具链: {tc['name']}）...")

    def _run(cmd: list, label: str) -> bool:
        print(f"  [{label}] " + " ".join(f'"{c}"' if " " in c else c for c in cmd))
        r = subprocess.run(
            cmd, cwd=str(build_dir),
            env=tc.get("env"),          # MSVC 需要环境变量；MinGW 传 None 继承当前
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            print(f"  [{label} 失败]\n{r.stderr[-2000:]}")
            return False
        return True

    # Configure
    if not _run(tc["configure_cmd"](project_dir), "configure"):
        return None

    # Build
    if not _run([tc["cmake"], "--build", "."], "build"):
        return None

    existing = (list(build_dir.rglob(f"{module_name}*.pyd")) +
                list(build_dir.rglob(f"{module_name}*.so")))
    if not existing:
        print(f"  [错误] 编译成功但找不到 {module_name}*.pyd / *.so")
        return None

    # 同上：inject sys.path → inject MinGW 运行时 PATH → 清缓存 → 加载新 .pyd
    _inject(existing[0].parent)
    _inject_path(tc.get("runtime_bin"))
    sys.modules.pop(module_name, None)
    return importlib.import_module(module_name)


# ── 工具链配置 ────────────────────────────────────────────────────────────────

def _resolve_toolchain(toolchain: str) -> dict | None:
    """返回工具链配置字典，找不到返回 None。"""
    if toolchain == "auto":
        if _msvc_available():
            return _make_msvc()
        if _mingw_available():
            return _make_mingw()
        return None
    if toolchain == "msvc":
        return _make_msvc() if _msvc_available() else None
    if toolchain == "mingw":
        return _make_mingw() if _mingw_available() else None
    raise ValueError(f"未知工具链: {toolchain!r}，可选 'auto' / 'msvc' / 'mingw'")


def _make_msvc() -> dict | None:
    """构建 MSVC 工具链配置（使用 CLion 内置 CMake / Ninja）。"""
    env = _msvc_env()
    if env is None:
        print("[警告] 无法从 vcvarsall.bat 获取 MSVC 环境变量")
        return None

    def configure_cmd(project_dir: Path) -> list:
        cmd = [
            MSVC_CMAKE, str(project_dir),
            f"-DCMAKE_MAKE_PROGRAM={MSVC_NINJA}",
            "-G", "Ninja",
            "-DCMAKE_BUILD_TYPE=Release",
            "-DCMAKE_CXX_COMPILER=cl.exe",
        ]
        # link.exe 可能被 MinGW 覆盖时显式指定，防止编译器/链接器混用
        if Path(MSVC_LD).exists():
            cmd.append(f"-DCMAKE_LINKER={MSVC_LD}")
        return cmd

    return {"name": "MSVC", "cmake": MSVC_CMAKE, "env": env, "configure_cmd": configure_cmd}


def _make_mingw() -> dict | None:
    """构建 MinGW 工具链配置（CMake/Ninja 用 CLion 内置，编译器用 g++）。"""
    cxx = _find_mingw_cxx()
    if cxx is None:
        return None

    def configure_cmd(project_dir: Path) -> list:
        return [
            MINGW_CMAKE, str(project_dir),
            f"-DCMAKE_MAKE_PROGRAM={MINGW_NINJA}",
            "-G", "Ninja",
            "-DCMAKE_BUILD_TYPE=Release",
            f"-DCMAKE_CXX_COMPILER={cxx}",
        ]

    mingw_bin = str(Path(cxx).parent)   # g++ 所在的 bin 目录，含运行时 DLL
    return {
        "name": f"MinGW ({cxx})",
        "cmake": MINGW_CMAKE,
        "env": None,
        "configure_cmd": configure_cmd,
        "runtime_bin": mingw_bin,       # import .pyd 前需要加入 PATH，否则找不到 MinGW 运行时 DLL
    }


# ── 内部工具 ──────────────────────────────────────────────────────────────────

def _inject(path: Path) -> None:
    """把目录加入 sys.path，让 import_module 能按名称找到 .pyd。"""
    s = str(path)
    if s not in sys.path:
        sys.path.insert(0, s)


def _inject_path(directory: str | None) -> None:
    """把 MinGW bin 目录注册为 DLL 搜索目录。

    MinGW 编译的 .pyd 依赖 libgcc_s_seh-1.dll / libstdc++-6.dll 等运行时，
    这些 DLL 在 MinGW bin 目录里。

    Python 3.8+ 在 Windows 上收紧了 DLL 搜索规则，修改 PATH 环境变量已不够，
    必须用 os.add_dll_directory() 显式注册，Windows 才能在 import 时找到这些 DLL。
    """
    if directory is None or not hasattr(os, "add_dll_directory"):
        return
    if Path(directory).exists():
        os.add_dll_directory(directory)
