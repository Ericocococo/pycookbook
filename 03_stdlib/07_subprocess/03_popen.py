"""subprocess —— Popen：精细控制子进程生命周期

标准库。Python 3.12。
运行: python 03_popen.py

Popen 是 subprocess 的底层 API，run() 内部就是调用它实现的。
需要以下场景时直接用 Popen：
  - 实时读取子进程输出（不等结束）
  - 向子进程发送数据（stdin 交互）
  - 非阻塞轮询进程状态
  - 更精细的生命周期控制（如超时后 kill 再清理）

演示：
  ① with 语句管理 Popen 生命周期（自动 wait + 关闭管道）
  ② communicate()：一次性收发，内置防死锁
  ③ stdin 管道：向子进程发送数据
  ④ poll()：非阻塞检查进程是否结束
  ⑤ wait()：阻塞等待，以及为什么要配合 communicate 而非直接 wait+read
"""
import subprocess
import time


def demo01_context_manager():
    """① with 语句管理 Popen

    术语：
      Popen   进程对象，代表一个正在运行的子进程
      __exit__ 时自动调用 wait()，等待子进程结束，并关闭 stdin/stdout/stderr 管道

    好习惯：始终用 with Popen(...) as proc，避免忘记 wait/close 导致僵尸进程。
    """
    print("① with Popen")

    with subprocess.Popen(
        ["python", "-c", "print('hello from popen')"],
        stdout=subprocess.PIPE,
        text=True,
    ) as proc:
        output = proc.stdout.read()   # 子进程输出少时，read() 一次读完
        print("  读到:", repr(output.strip()))

    # 退出 with 块后，proc.returncode 已被填充
    print("  退出 with 后 returncode:", proc.returncode)


def demo02_communicate():
    """② communicate()：推荐方式，自动防止死锁

    术语：
      死锁   父进程等子进程写完 stdout，子进程等父进程读 stderr（或反之），
             双方阻塞，程序卡死。
      communicate()  在内部用线程同时读 stdout 和 stderr，避免死锁。
                     适合输出量"有限"的情况（全部读入内存）。

    返回：(stdout, stderr) 元组（text=True 时是 str，否则是 bytes）
    """
    print("\n② communicate()")

    proc = subprocess.Popen(
        ["python", "-c",
         "import sys; print('标准输出'); print('标准错误', file=sys.stderr)"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = proc.communicate()   # 等待结束，同时读完两条管道
    print("  stdout:", repr(stdout.strip()))
    print("  stderr:", repr(stderr.strip()))
    print("  returncode:", proc.returncode)


def demo03_stdin():
    """③ stdin 管道：向子进程发送数据

    communicate(input=...) 是发送 stdin 的最安全方式：
      - 发送完后自动关闭 stdin（子进程收到 EOF，不会阻塞等更多数据）
      - 同时读 stdout/stderr（防死锁）

    input= 接受 str（text=True 时）或 bytes。
    """
    print("\n③ stdin 输入")

    proc = subprocess.Popen(
        ["python", "-c",
         "import sys\n"
         "data = sys.stdin.read().strip()\n"
         "print(f'子进程收到: {data!r}')"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    stdout, _ = proc.communicate(input="你好，子进程\n")
    print("  子进程回复:", stdout.strip())


def demo04_stdin_interactive():
    """③-补 多行交互（simulate）

    用 communicate 一次性发多行，而不是反复调用 proc.stdin.write()。
    反复调用 write() 很容易导致死锁（子进程在等你发完，你在等子进程回复）。
    """
    print("\n③-补 多行 stdin 发送")

    script = (
        "import sys\n"
        "for line in sys.stdin:\n"
        "    print('  →', line.strip())\n"
    )
    proc = subprocess.Popen(
        ["python", "-c", script],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    # 一次性发送所有输入
    stdin_data = "第一行\n第二行\n第三行\n"
    stdout, _ = proc.communicate(input=stdin_data)
    print(stdout, end="")


def demo05_poll():
    """④ poll()：非阻塞检查进程状态

    术语：
      poll()  立即返回，不阻塞：
                - 子进程仍在运行 → 返回 None
                - 子进程已结束   → 返回 returncode（整数）

    适合：父进程需要同时做别的事情，周期性检查子进程是否结束。
    """
    print("\n④ poll() 非阻塞轮询")

    proc = subprocess.Popen(
        ["python", "-c", "import time; time.sleep(0.5); print('done')"],
        stdout=subprocess.PIPE,
        text=True,
    )

    for i in range(10):
        code = proc.poll()
        if code is None:
            print(f"  轮询 {i}: 进程仍在运行...")
        else:
            print(f"  轮询 {i}: 进程结束，returncode={code}")
            break
        time.sleep(0.1)

    proc.wait()   # 保证完全回收，即使已经结束也无害


def demo06_wait_pitfall():
    """⑤ wait() 与"PIPE + wait"死锁陷阱

    wait() 阻塞直到子进程结束。
    但！如果子进程输出量大 + stdout=PIPE + 父进程 wait() 而不读管道：
      管道缓冲区被填满 → 子进程阻塞在 write → 父进程 wait 永远等不到结束 → 死锁

    正确做法：
      输出量少   → communicate()（内部自动读完）
      需要实时   → Popen + for line in proc.stdout 迭代
      只等结束   → 不用 PIPE（不捕获输出）时，wait() 才安全
    """
    print("\n⑤ wait() 安全用法")

    # 安全：不捕获输出（没有 PIPE），直接 wait
    proc = subprocess.Popen(
        ["python", "-c", "import time; time.sleep(0.2)"],
        # 没有 stdout=PIPE，不会死锁
    )
    try:
        code = proc.wait(timeout=2)   # 最多等 2 秒
        print("  进程结束，returncode:", code)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()   # kill 后也要 communicate 清理
        print("  超时，已强制终止")


if __name__ == "__main__":
    demo01_context_manager()
    demo02_communicate()
    demo03_stdin()
    demo04_stdin_interactive()
    demo05_poll()
    demo06_wait_pitfall()
