"""subprocess —— subprocess.run 全面用法

标准库。Python 3.12。
运行: python 01_run.py

subprocess.run 是启动子进程的首选 API（Python 3.5+）：
它等待子进程结束后返回 CompletedProcess 对象。

演示：
  ① 基础调用：list 参数 vs string 参数，以及为什么推荐 list
  ② CompletedProcess：returncode / stdout / stderr 字段
  ③ capture_output + text：捕获并解码输出（最常用组合）
  ④ check=True：非零退出码自动抛 CalledProcessError
  ⑤ cwd / env：指定工作目录和环境变量
  ⑥ timeout：设置超时，超时抛 TimeoutExpired
"""
import subprocess
import sys
import os
from pathlib import Path


def demo01_basic():
    """① list 参数 vs string 参数

    术语：
      args    subprocess 的第一个参数，推荐传 list（每个元素是一个 token）
      token   命令行中以空格分隔的最小单元，如 ["git", "log"] 有两个 token
    """
    print("① 基础调用")

    # 推荐：list 参数，每个 token 独立，不需要 shell，安全
    r = subprocess.run(["python", "--version"])
    print("  list 参数 returncode:", r.returncode)

    # 不推荐：string 参数 + shell=True，方便但有注入风险（见 05_advanced.py）
    # subprocess.run("python --version", shell=True)

    # 子进程的输出默认直接打印到终端（不捕获）
    print("  不捕获时输出直接打到终端 ↑")


def demo02_completed_process():
    """② CompletedProcess 返回对象"""
    print("② CompletedProcess 字段")

    r = subprocess.run(
        ["python", "-c", "import sys; print('hello'); sys.exit(0)"],
        capture_output=True,   # stdout=PIPE + stderr=PIPE 的缩写
        text=True,             # 把 bytes 解码为 str（用系统默认编码）
    )
    print("  类型:", type(r))
    print("  r.returncode:", r.returncode)   # 0 = 成功
    print("  r.stdout:", repr(r.stdout))     # 捕获的标准输出
    print("  r.stderr:", repr(r.stderr))     # 捕获的标准错误
    print("  r.args:", r.args)              # 原始命令


def demo03_capture_text():
    """③ capture_output=True + text=True（最常用组合）

    术语：
      capture_output  = stdout=PIPE + stderr=PIPE 的简写
      text=True       让 stdout/stderr 自动解码为 str；否则是 bytes
    """
    print("③ 捕获输出")

    # 获取 git 最近 3 条提交（在 pycookbook 目录执行）
    repo = Path(__file__).parent.parent.parent
    r = subprocess.run(
        ["git", "log", "--oneline", "-3"],
        capture_output=True,
        text=True,
        cwd=str(repo),         # 在 repo 根目录运行
    )
    if r.returncode == 0:
        print("  git log 输出:")
        for line in r.stdout.splitlines():
            print("   ", line)
    else:
        print("  git 失败:", r.stderr.strip())


def demo04_check():
    """④ check=True：非零 returncode 自动抛异常

    术语：
      CalledProcessError  check=True 时，子进程退出码非 0 抛出的异常
                          包含 returncode / cmd / stdout / stderr 属性
    """
    print("④ check=True")

    # 正常情况：returncode=0，不抛异常
    r = subprocess.run(["python", "-c", "pass"], check=True,
                       capture_output=True, text=True)
    print("  正常退出 returncode:", r.returncode)

    # 出错情况：returncode!=0，抛 CalledProcessError
    try:
        subprocess.run(
            ["python", "-c", "import sys; sys.exit(42)"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print("  捕获到 CalledProcessError:")
        print("    returncode:", e.returncode)
        print("    cmd:", e.cmd)


def demo05_cwd_env():
    """⑤ cwd / env：工作目录和环境变量

    术语：
      cwd   current working directory，子进程的起始工作目录
      env   子进程继承的完整环境变量 dict；传 None 则继承父进程的
    """
    print("⑤ cwd / env")

    # cwd：子进程在指定目录里执行
    r = subprocess.run(["python", "-c", "import os; print(os.getcwd())"],
                       capture_output=True, text=True,
                       cwd="C:/Windows")
    print("  cwd=C:/Windows 时 getcwd():", r.stdout.strip())

    # env：向子进程传递自定义环境变量
    custom_env = os.environ.copy()      # 先拷贝当前环境（否则 PATH 等也会丢失）
    custom_env["MY_VAR"] = "hello_sub"
    r = subprocess.run(
        ["python", "-c", "import os; print(os.getenv('MY_VAR'))"],
        capture_output=True, text=True,
        env=custom_env,
    )
    print("  子进程读到 MY_VAR:", r.stdout.strip())


def demo06_timeout():
    """⑥ timeout：超时保护

    术语：
      TimeoutExpired  超时后抛出的异常；进程并不会自动被杀死，需手动 kill
    """
    print("⑥ timeout")

    try:
        # 让子进程睡 10 秒，但我们只等 1 秒
        subprocess.run(
            ["python", "-c", "import time; time.sleep(10)"],
            timeout=1,
            capture_output=True,
        )
    except subprocess.TimeoutExpired as e:
        print("  超时！等了:", e.timeout, "秒")
        print("  命令:", e.cmd)
        # 注意：TimeoutExpired 后子进程仍在运行，run() 内部会自动 kill 它


if __name__ == "__main__":
    demo01_basic()
    print()
    demo02_completed_process()
    print()
    demo03_capture_text()
    print()
    demo04_check()
    print()
    demo05_cwd_env()
    print()
    demo06_timeout()
