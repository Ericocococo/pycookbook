"""subprocess —— 进阶：超时清理 / 后台进程 / 注入陷阱 / 无窗口 / asyncio

标准库。Python 3.12。
运行: python 05_advanced.py

演示：
  ① 超时后完整清理流程（kill + communicate）
  ② 后台进程：fire-and-forget，不阻塞父进程
  ③ shell 注入陷阱：为什么用户输入不能直接拼进命令
  ④ Windows 无窗口运行（CREATE_NO_WINDOW）
  ⑤ asyncio 异步子进程：在 async 程序里并发启动多进程
"""
import subprocess
import sys
import time


# ---------------------------------------------------------------------------
# ① 超时清理
# ---------------------------------------------------------------------------

def demo01_timeout_cleanup():
    """① 超时后完整清理

    run() 超时会自动 kill 子进程。
    但 Popen.communicate(timeout=N) 超时后，子进程并不会自动终止，
    需要手动 kill → communicate（清空管道缓冲，避免僵尸进程）。

    术语：
      kill()       强制终止，立即停止（Unix=SIGKILL，Windows=TerminateProcess）
      terminate()  请求优雅退出（Unix=SIGTERM；Windows 同 kill）
      僵尸进程     子进程已结束，但父进程未 wait → 资源未回收
    """
    print("① 超时清理")

    proc = subprocess.Popen(
        ["python", "-c", "import time; time.sleep(10)"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        stdout, stderr = proc.communicate(timeout=0.5)
        print("  正常结束（不会走到这里）")
    except subprocess.TimeoutExpired:
        print("  超时！开始清理...")
        proc.kill()                           # 步骤一：强制终止
        stdout, stderr = proc.communicate()   # 步骤二：清空管道缓冲，回收资源
        print(f"  清理完毕，returncode={proc.returncode}")
        # returncode < 0 表示被信号终止（Unix）；Windows 通常是 1


# ---------------------------------------------------------------------------
# ② 后台进程
# ---------------------------------------------------------------------------

def demo02_background():
    """② 后台进程（fire-and-forget）

    不调用 wait()/communicate()，子进程与父进程并发运行。
    父进程退出时，子进程可能变成孤儿进程（由操作系统 init 接管继续运行）。

    术语：
      PID           进程 ID，操作系统分配的唯一编号
      孤儿进程       父进程先退出，子进程继续存活
      proc.pid      Popen 对象持有的子进程 PID

    注意：若需要后台进程的结果，最终要调用 proc.wait() 回收，否则是资源泄漏。
    """
    print("\n② 后台进程")

    # 启动一个耗时任务，父进程继续做别的事
    proc = subprocess.Popen(
        ["python", "-c",
         "import time; time.sleep(0.5); print('后台任务完成')"],
        stdout=subprocess.PIPE,
        text=True,
    )
    print(f"  后台进程已启动，PID={proc.pid}，父进程继续...")

    for i in range(3):
        print(f"  父进程工作中 [{i}]")
        time.sleep(0.2)

    # 稍后收结果
    out, _ = proc.communicate()
    print("  后台进程输出:", out.strip())
    print("  后台进程 returncode:", proc.returncode)


# ---------------------------------------------------------------------------
# ③ shell 注入陷阱
# ---------------------------------------------------------------------------

def demo03_shell_injection():
    """③ shell 注入陷阱

    当 shell=True 且把用户输入拼进命令字符串时，
    恶意输入可以通过 ; & | 等 shell 特殊字符注入任意命令。

    原则：
      永远不要把用户输入直接拼进 shell=True 的命令字符串。
      改用 list 参数（shell 默认 False），每个参数独立传给程序，不经 shell 解析。
    """
    print("\n③ shell 注入陷阱")

    # 假设这是用户提供的文件名（恶意构造）
    malicious = "a.txt & python -c \"print('注入成功！')\""

    print("  [危险] shell=True + 字符串拼接:")
    print(f"    命令字符串: type {malicious}")
    print("    '&' 后面的命令会被 shell 执行！（这里不实际运行，防止演示出错）")
    # 取消下面这行注释可以看到注入效果：
    # subprocess.run(f"type {malicious}", shell=True)

    print()
    print("  [安全] list 参数，shell=False（默认）:")
    r = subprocess.run(
        # 恶意字符串整体作为一个参数传给 python，不被 shell 解析
        ["python", "-c", f"print('收到参数:', {repr(malicious)})"],
        capture_output=True,
        text=True,
    )
    print("   ", r.stdout.strip())
    print("    '& python ...' 只是一个普通字符串，没有被执行")


# ---------------------------------------------------------------------------
# ④ Windows 无窗口运行
# ---------------------------------------------------------------------------

def demo04_windows_no_window():
    """④ Windows 无窗口运行

    Windows 上启动 .exe / .bat 时，默认会弹出黑色控制台窗口（闪一下）。
    在 GUI 程序或服务里调用子进程时，通常不想弹窗。

    术语：
      creationflags           Windows 进程创建标志位（整数，可按位 OR 组合）
      CREATE_NO_WINDOW        不创建控制台窗口（子进程有控制台但不可见）
      DETACHED_PROCESS        完全与父进程控制台分离（用于长期后台进程）

    Python 3.7+ 可以直接用 subprocess.CREATE_NO_WINDOW 常量。
    """
    print("\n④ Windows 无窗口运行")

    if sys.platform != "win32":
        print("  （跳过：仅 Windows 适用）")
        return

    r = subprocess.run(
        ["python", "-c", "print('无窗口运行成功')"],
        capture_output=True,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW,   # Python 3.7+
    )
    print("  结果:", r.stdout.strip())

    # 组合标志（如无窗口 + 高优先级）：
    # ABOVE_NORMAL_PRIORITY_CLASS = 0x00008000
    # creationflags = subprocess.CREATE_NO_WINDOW | 0x00008000


# ---------------------------------------------------------------------------
# ⑤ asyncio 异步子进程
# ---------------------------------------------------------------------------

def demo05_asyncio():
    """⑤ asyncio 异步子进程

    asyncio 提供 create_subprocess_exec（对应 Popen），
    在 async 函数里用 await 等待子进程，不阻塞事件循环。

    适用场景：
      - Web 服务器（FastAPI/aiohttp）里调用外部命令
      - 同时并发启动多个子进程，等所有子进程都完成

    注意：asyncio.subprocess 不支持 text=True，
    stdout 是 bytes，需要手动 .decode()。
    """
    print("\n⑤ asyncio 异步子进程")

    import asyncio

    async def run_one(cmd, label):
        """运行一条命令并返回输出"""
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        return label, stdout.decode().strip()

    async def main():
        # 并发启动 3 个子进程（asyncio.gather 等所有完成）
        results = await asyncio.gather(
            run_one(["python", "-c", "import time; time.sleep(0.2); print('A')"], "A"),
            run_one(["python", "-c", "import time; time.sleep(0.1); print('B')"], "B"),
            run_one(["python", "-c", "print('C')"], "C"),
        )
        for label, out in results:
            print(f"  进程 {label} 输出: {out}")

    asyncio.run(main())
    print("  （3 个进程并发，总耗时约等于最慢的那个）")


if __name__ == "__main__":
    demo01_timeout_cleanup()
    demo02_background()
    demo03_shell_injection()
    demo04_windows_no_window()
    demo05_asyncio()
