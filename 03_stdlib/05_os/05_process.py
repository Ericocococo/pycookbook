"""os —— 进程信息与系统常量

标准库,无需安装,Python 3.12。运行: python 05_process.py

涵盖:os.name / sep / pathsep 等常量 / getpid / cpu_count / urandom / os.times
"""
import base64
import os
import subprocess
import sys
from pathlib import Path

WORK = Path(__file__).parent / "data"


def setup():
    """准备工作目录(本脚本无临时文件产出,仅保持目录约定)"""
    WORK.mkdir(exist_ok=True)


def demo01_constants():
    """① os 系统常量:name / sep / altsep / linesep / pathsep / curdir / pardir / devnull / extsep"""
    print("① os 系统常量:")
    print("  os.name  :", repr(os.name),
          "    (nt=Windows, posix=Linux/Mac)")
    print("  os.sep   :", repr(os.sep),
          "    (路径分隔符:Win='\\\\' / Unix='/')")
    print("  os.altsep:", repr(os.altsep),
          "  (备用分隔符:Win='/' / 其他=None)")
    print("  os.linesep:", repr(os.linesep),
          " (行分隔符:Win='\\r\\n' / Unix='\\n')")
    print("  os.pathsep:", repr(os.pathsep),
          " (PATH 目录间分隔:Win=';' / Unix=':')")
    print("  os.curdir :", repr(os.curdir),
          "    (当前目录符号 '.')")
    print("  os.pardir :", repr(os.pardir),
          "   (父目录符号 '..')")
    print("  os.devnull:", repr(os.devnull),
          "  (空设备:Win='nul' / Unix='/dev/null')")
    print("  os.extsep :", repr(os.extsep),
          "    (扩展名分隔符 '.')")


def demo02_process_info():
    """② 进程信息:getpid / getppid / cpu_count / getlogin"""
    print("② 进程信息:")
    pid  = os.getpid()
    ppid = os.getppid()
    cpus = os.cpu_count()
    print("  os.getpid()   :", pid,  type(pid),  "(当前进程 PID)")
    print("  os.getppid()  :", ppid, type(ppid), "(父进程 PID)")
    print("  os.cpu_count():", cpus, type(cpus), "(逻辑 CPU 核心数,含超线程)")

    try:
        login = os.getlogin()
        print("  os.getlogin() :", login, "(登录用户名)")
    except OSError as e:
        # 某些环境(CI/容器/无 tty)getlogin() 会失败
        fallback = os.environ.get("USERNAME") or os.environ.get("USER", "unknown")
        print("  os.getlogin() 不可用:", e)
        print("  fallback via environ:", fallback)


def demo03_urandom():
    """③ os.urandom:生成密码学安全随机字节,转 hex / int"""
    print("③ os.urandom(密码学安全随机字节,适合 token/nonce/key):")

    raw = os.urandom(16)                     # 16 字节 = 128 位
    print("  urandom(16) raw   :", raw, type(raw))
    print("  转 hex             :", raw.hex())
    print("  转大整数           :", int.from_bytes(raw, "big"))
    print("  转 base64          :", base64.b64encode(raw).decode())

    # 生成 256 位(32字节)安全 token
    token = os.urandom(32).hex()             # 64 个十六进制字符
    print("  32字节 token(hex)  :", token)
    print("  token 长度         :", len(token), "字符")

    # 与 random 模块对比(random 不是密码学安全的)
    print()
    print("  注意:os.urandom 密码学安全,random 模块不安全,勿用于密码/token")


def demo04_system_vs_subprocess():
    """④ os.system vs subprocess（简单对比,不深入）"""
    print("④ os.system vs subprocess:")

    # os.system:简单,但只返回退出码,无法捕获输出
    print("  -- os.system 输出(直接打印到终端) --")
    sys.stdout.flush()                       # 先 flush,再启动子进程,保证输出顺序
    code = os.system(f"{sys.executable} -c \"print('hello from os.system')\"")
    print("  -- os.system 退出码:", code, "(0 = 成功) --")

    print()

    # subprocess.run:可捕获输出、设置超时、安全传参数
    result = subprocess.run(
        [sys.executable, "-c", "print('hello from subprocess')"],
        capture_output=True,
        text=True,
    )
    print("  subprocess.run stdout  :", result.stdout.strip())
    print("  subprocess.run returncode:", result.returncode)

    print()
    print("  对比:")
    print("    os.system     —— 一行命令、无需捕获输出时可用;底层走 shell")
    print("    subprocess    —— 需要捕获输出 / 传参数 / 设超时 / 安全性时必选")


def demo05_times():
    """⑤ os.times:进程用户/系统 CPU 时间"""
    print("⑤ os.times(进程 CPU 时间消耗):")
    t1 = os.times()
    print("  计算前 times():", t1)
    print("  user   :", t1.user,   "秒(用户态 CPU 时间)")
    print("  system :", t1.system, "秒(内核态 CPU 时间)")
    print("  elapsed:", t1.elapsed, "秒(挂钟时间,部分平台为 0)")

    # 做点纯计算让 user 时间增加
    _ = sum(i * i for i in range(1_000_000))

    t2 = os.times()
    print()
    print("  计算后 user:", t2.user, "(应略有增加)")
    print("  user 差值  :", round(t2.user - t1.user, 4), "秒")


if __name__ == "__main__":
    setup()
    demo01_constants()
    print()
    demo02_process_info()
    print()
    demo03_urandom()
    print()
    demo04_system_vs_subprocess()
    print()
    demo05_times()
