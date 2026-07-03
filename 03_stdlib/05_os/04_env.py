"""os —— 环境变量

标准库,无需安装,Python 3.12。运行: python 04_env.py

os.environ 是一个类 Mapping 对象:对它的修改立即生效于本进程,
子进程(subprocess)启动时继承修改后的快照。
"""
import os
import subprocess
import sys
from pathlib import Path

WORK = Path(__file__).parent / "data"


def setup():
    """准备工作目录(本脚本无临时文件产出,仅保持目录约定)"""
    WORK.mkdir(exist_ok=True)


def demo01_read():
    """① os.environ 读取:keys() / __getitem__ / get(default)"""
    print("① os.environ 读取:")
    print("  类型:", type(os.environ))

    # keys():所有变量名(懒惰视图,不是列表)
    all_keys = list(os.environ.keys())
    print("  变量总数:", len(all_keys))
    print("  前 5 个键:", all_keys[:5])

    # __getitem__:键不存在则 KeyError
    try:
        path_val = os.environ["PATH"]
        print("  PATH 前 60 字符:", path_val[:60], "...")
    except KeyError as e:
        print("  PATH 不存在:", e)

    # get:不存在时返回默认值,不抛异常
    missing = os.environ.get("NOT_EXIST_VAR_XYZ_DEMO", "默认值")
    print("  get('NOT_EXIST...', '默认值'):", missing)

    # in 检测:更高效的存在性判断
    print("  'PATH' in environ:", "PATH" in os.environ)
    print("  'GHOST_VAR' in environ:", "GHOST_VAR_XYZ" in os.environ)


def demo02_write_del():
    """② os.getenv / os.environ[] 写入 / del / pop"""
    print("② 写入、删除环境变量:")

    # os.getenv 等价于 os.environ.get
    val = os.getenv("NOT_EXIST_VAR_XYZ_DEMO", "getenv默认值")
    print("  os.getenv('NOT_EXIST...', ...):", val)

    # 写入新变量(值必须是字符串)
    os.environ["MY_DEMO_VAR"] = "hello_os"
    print("  写入后 MY_DEMO_VAR:", os.environ["MY_DEMO_VAR"])

    # 修改已有变量
    os.environ["MY_DEMO_VAR"] = "updated_value"
    print("  修改后 MY_DEMO_VAR:", os.environ["MY_DEMO_VAR"])

    # del:删除变量,不存在则 KeyError
    del os.environ["MY_DEMO_VAR"]
    print("  del 后 MY_DEMO_VAR 存在:", "MY_DEMO_VAR" in os.environ)

    # pop:删除并返回值,键不存在时返回默认值(不报错)
    os.environ["POP_ME"] = "bye"
    popped = os.environ.pop("POP_ME", "not_found")
    print("  pop('POP_ME')        :", popped)
    print("  pop('GHOST_VAR_XYZ') :", os.environ.pop("GHOST_VAR_XYZ", "not_found"))


def demo03_expandvars():
    """③ os.path.expandvars 展开字符串中的变量"""
    print("③ os.path.expandvars:")
    os.environ["GREET_DEMO"] = "world"

    # Windows 支持 %VAR% 写法;Unix/Windows 均支持 $VAR 写法
    if os.name == "nt":
        tpl_pct = "Hello, %GREET_DEMO%!"
        tpl_dol = "Hello, $GREET_DEMO!"
        print("  expandvars('%GREET_DEMO%'):", os.path.expandvars(tpl_pct))
        print("  expandvars('$GREET_DEMO') :", os.path.expandvars(tpl_dol))
    else:
        print("  expandvars('$GREET_DEMO')  :", os.path.expandvars("Hello, $GREET_DEMO!"))
        print("  expandvars('${GREET_DEMO}'):", os.path.expandvars("Hello, ${GREET_DEMO}!"))

    # 未定义的变量原样保留(不报错)
    if os.name == "nt":
        undef_tpl = "%UNDEFINED_XYZ_DEMO%"
    else:
        undef_tpl = "$UNDEFINED_XYZ_DEMO"
    print("  未定义变量原样保留:", os.path.expandvars(undef_tpl))

    del os.environ["GREET_DEMO"]


def demo04_common_vars():
    """④ 常用环境变量:PATH / HOME / TEMP / USERNAME / PYTHONPATH 等"""
    print("④ 常用环境变量:")

    # (变量名, 说明, 典型值截断长度)
    vars_info = [
        ("PATH",             "可执行文件搜索路径(多个目录用 pathsep 分隔)", 60),
        ("HOME",             "用户主目录(Linux/Mac)",                       80),
        ("USERPROFILE",      "用户主目录(Windows)",                          80),
        ("TEMP",             "临时文件目录(Windows)",                         80),
        ("TMPDIR",           "临时文件目录(Linux/Mac)",                       80),
        ("USERNAME",         "当前用户名(Windows)",                          40),
        ("USER",             "当前用户名(Linux/Mac)",                        40),
        ("PYTHONPATH",       "Python 模块搜索路径(可选,未设置则无此变量)",    60),
        ("PYTHONIOENCODING", "Python IO 编码(如 utf-8)",                     40),
        ("VIRTUAL_ENV",      "激活的虚拟环境路径(conda/venv 激活时存在)",     60),
    ]
    for var, desc, limit in vars_info:
        val = os.environ.get(var, "(未设置)")
        display = val[:limit] + ("..." if len(val) > limit else "")
        print(f"  {var:<22}: {display}")


def demo05_subprocess_inherit():
    """⑤ 子进程继承:修改 os.environ 对 subprocess 的影响"""
    print("⑤ 子进程继承 os.environ:")

    # 父进程写入变量
    os.environ["DEMO_PARENT_VAR"] = "from_parent_process"

    # 子进程自动继承父进程的 environ
    result = subprocess.run(
        [sys.executable, "-c",
         "import os; print(os.environ.get('DEMO_PARENT_VAR', 'NOT_FOUND'))"],
        capture_output=True, text=True,
    )
    print("  子进程继承读到:", result.stdout.strip())

    # 用 env 参数传递自定义快照(覆盖指定变量,不影响父进程)
    custom_env = os.environ.copy()
    custom_env["DEMO_PARENT_VAR"] = "overridden_in_child"
    result2 = subprocess.run(
        [sys.executable, "-c",
         "import os; print(os.environ.get('DEMO_PARENT_VAR', 'NOT_FOUND'))"],
        capture_output=True, text=True,
        env=custom_env,
    )
    print("  自定义 env 快照传递:", result2.stdout.strip())

    # 父进程的变量没有被子进程修改影响
    print("  父进程变量仍是:", os.environ["DEMO_PARENT_VAR"])

    del os.environ["DEMO_PARENT_VAR"]


if __name__ == "__main__":
    setup()
    demo01_read()
    print()
    demo02_write_del()
    print()
    demo03_expandvars()
    print()
    demo04_common_vars()
    print()
    demo05_subprocess_inherit()
