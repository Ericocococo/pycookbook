"""共享 CMake 编译辅助工具 —— 供各 demo.py import，不直接运行。

工具链（与 cppcookbook 一致）：
  MSVC  cl.exe  D:/Program Files/Microsoft Visual Studio/18/Community/...
  CMake 4.2.2   D:/ProgramData/JetBrains/CLion20260101/bin/cmake/...
  Ninja 1.13.2  D:/ProgramData/JetBrains/CLion20260101/bin/ninja/...
  Python 3.12   D:/ProgramData/anaconda3/envs/quant312/python.exe
"""
import importlib
import subprocess
import sys
from pathlib import Path

# ── 路径常量 ──────────────────────────────────────────────────
PYTHON  = r"D:\ProgramData\anaconda3\envs\quant312\python.exe"
CMAKE   = r"D:\ProgramData\JetBrains\CLion20260101\bin\cmake\win\x64\bin\cmake.exe"
NINJA   = r"D:\ProgramData\JetBrains\CLion20260101\bin\ninja\win\x64\ninja.exe"
VCVARS  = (r"D:\Program Files\Microsoft Visual Studio\18\Community"
           r"\VC\Auxiliary\Build\vcvarsall.bat")


def _msvc_env() -> dict | None:
    """通过 vcvarsall.bat amd64 获取 MSVC 完整环境变量。"""
    if not Path(VCVARS).exists():
        print(f"[警告] 找不到 vcvarsall.bat: {VCVARS}")
        return None
    cmd = f'"{VCVARS}" amd64 && set'
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    env: dict[str, str] = {}
    for line in r.stdout.splitlines():
        if '=' in line:
            k, _, v = line.partition('=')
            env[k.strip()] = v.strip()
    return env if env else None


def build_and_import(project_dir: Path, module_name: str):
    """
    用 CMake + MSVC + Ninja 编译 pybind11 扩展，注入 sys.path 后返回模块对象。

    project_dir : CMakeLists.txt 所在目录（各配方子文件夹）
    module_name : PYBIND11_MODULE 里声明的模块名（如 "pb_basic"）
    返回         : 模块对象；编译失败时返回 None 并打印错误。
    """
    build_dir = project_dir / "build"
    build_dir.mkdir(exist_ok=True)

    # 已有产物 → 直接 import
    existing = (list(build_dir.rglob(f"{module_name}*.pyd")) +
                list(build_dir.rglob(f"{module_name}*.so")))
    if existing:
        _inject(existing[0].parent)
        sys.modules.pop(module_name, None)
        try:
            return importlib.import_module(module_name)
        except ImportError:
            pass  # 产物失效，重新编译

    print(f"[CMake] 编译 {module_name} ...")
    env = _msvc_env()
    if env is None:
        print("  [跳过] 无法获取 MSVC 环境，请确认 Visual Studio 已安装")
        return None

    def _run(cmd: list, label: str) -> bool:
        r = subprocess.run(
            cmd, cwd=str(build_dir), env=env,
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            print(f"  [{label} 失败]\n{r.stderr[-2000:]}")
            return False
        return True

    # Configure（Ninja + MSVC cl.exe）
    if not _run([
        CMAKE, str(project_dir),
        f"-DCMAKE_MAKE_PROGRAM={NINJA}",
        "-G", "Ninja",
        "-DCMAKE_BUILD_TYPE=Release",
        "-DCMAKE_CXX_COMPILER=cl.exe",
    ], "configure"):
        return None

    # Build
    if not _run([CMAKE, "--build", "."], "build"):
        return None

    existing = (list(build_dir.rglob(f"{module_name}*.pyd")) +
                list(build_dir.rglob(f"{module_name}*.so")))
    if not existing:
        print(f"  [错误] 编译成功但找不到 {module_name}*.pyd")
        return None

    _inject(existing[0].parent)
    sys.modules.pop(module_name, None)
    return importlib.import_module(module_name)


def _inject(path: Path) -> None:
    s = str(path)
    if s not in sys.path:
        sys.path.insert(0, s)
