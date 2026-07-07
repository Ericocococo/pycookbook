"""subprocess —— 管道链：Python 原生替代 shell 管道

标准库。Python 3.12。
运行: python 04_pipe.py

shell 管道：cmd1 | cmd2
  cmd1 的 stdout 直接连到 cmd2 的 stdin，操作系统负责传输。

Python 原生管道：p1.stdout → p2.stdin
  父进程把 p1 的 PIPE stdout 接到 p2 的 stdin，
  比 shell=True 更安全、可移植、每个进程 returncode 都可以单独检查。

演示：
  ① 两进程管道（基础：producer | consumer）
  ② 三进程管道链（producer | filter | reducer）
  ③ 死锁陷阱与 communicate 安全写法
  ④ shell=True 管道对比（简单但有风险）
"""
import subprocess


def demo01_two_process_pipe():
    """① 两进程管道

    类比：python -c "..." | python -c "..."

    关键两步：
      1. p2 的 stdin=p1.stdout（把管道接起来）
      2. p1.stdout.close()（父进程关掉自己持有的引用）
         → 这样 p2 才能在 p1 结束后收到 EOF，不会永远阻塞等输入
    """
    print("① 两进程管道")

    # producer：输出 5 行
    p1 = subprocess.Popen(
        ["python", "-c",
         "for i in range(5): print(f'行{i}')"],
        stdout=subprocess.PIPE,
        text=True,
    )
    # consumer：统计行数
    p2 = subprocess.Popen(
        ["python", "-c",
         "import sys; lines = sys.stdin.readlines(); print(f'共 {len(lines)} 行')"],
        stdin=p1.stdout,          # 关键①：管道接起来
        stdout=subprocess.PIPE,
        text=True,
    )
    p1.stdout.close()             # 关键②：父进程关自己的引用，p2 才能感知 EOF

    output, _ = p2.communicate()
    p1.wait()

    print("  结果:", output.strip())


def demo02_three_process_pipe():
    """② 三进程管道链（producer | filter | reducer）

    类比：producer | grep even | sum
    每一级关掉父进程自己的引用，让下一级能感知 EOF。
    """
    print("\n② 三进程管道链")

    # 生产者：输出 0-9，每行一个数字
    producer = subprocess.Popen(
        ["python", "-c",
         "for i in range(10): print(i)"],
        stdout=subprocess.PIPE,
        text=True,
    )
    # 过滤器：只保留偶数
    filter_ = subprocess.Popen(
        ["python", "-c",
         "import sys\n"
         "for line in sys.stdin:\n"
         "    n = int(line.strip())\n"
         "    if n % 2 == 0:\n"
         "        print(n)\n"],
        stdin=producer.stdout,
        stdout=subprocess.PIPE,
        text=True,
    )
    producer.stdout.close()       # 让 filter 能感知 producer 的 EOF

    # 汇总：求和
    reducer = subprocess.Popen(
        ["python", "-c",
         "import sys\n"
         "nums = [int(l) for l in sys.stdin]\n"
         "print('偶数之和:', sum(nums))"],
        stdin=filter_.stdout,
        stdout=subprocess.PIPE,
        text=True,
    )
    filter_.stdout.close()        # 让 reducer 能感知 filter 的 EOF

    output, _ = reducer.communicate()
    filter_.wait()
    producer.wait()

    print("  结果:", output.strip())   # 0+2+4+6+8 = 20


def demo03_deadlock_safe():
    """③ 死锁陷阱与安全写法

    死锁场景（两进程管道）：
      p1 → PIPE → p2
      如果 p1 输出量超过管道缓冲区（通常约 64KB）：
        p1 阻塞在 write（管道满了，写不进去）
        父进程却在 p1.wait() 或 p1.stdout.read()（没人在读管道）
        → 双方都在等对方 → 死锁

    安全写法：
      方案 A：communicate()（内置线程同时读，推荐）
      方案 B：先 communicate 收完 p1 全部输出，再用 input= 喂给 p2

    注意：方案 B 会把中间结果整个放入内存，适合数据量可控的场景。
    """
    print("\n③ 死锁安全写法（communicate 版）")

    # 生产大量输出（100 行，每行 100 字节，约 10KB，足以演示）
    p1 = subprocess.Popen(
        ["python", "-c",
         "for i in range(100): print('x' * 100)"],
        stdout=subprocess.PIPE,
        text=True,
    )
    # communicate() 内部用线程并发读，不会死锁
    p1_out, _ = p1.communicate()

    # 把 p1 的输出通过 input= 喂给 p2
    p2 = subprocess.Popen(
        ["python", "-c",
         "import sys; data = sys.stdin.read(); print(f'收到 {len(data)} 字节')"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    p2_out, _ = p2.communicate(input=p1_out)
    print("  安全管道结果:", p2_out.strip())


def demo04_shell_pipe_vs_python():
    """④ shell=True 管道 vs Python 原生管道

    shell=True 简便，但：
      1. 有命令注入风险（见 05_advanced.py）
      2. 跨平台差异大（Windows cmd 和 bash 语法不同）
      3. 只能拿到最后一条命令的 returncode（中间失败不易察觉）
      4. 调试困难（命令是一整个字符串）

    Python 原生管道：
      ✓ 安全（不经过 shell 解析）
      ✓ 可移植（纯 Python API）
      ✓ 每个进程的 returncode 都可以单独检查
    """
    print("\n④ shell=True 管道 vs Python 原生")

    # shell=True：简单但有局限
    r = subprocess.run(
        # Windows 用 & 分隔；Unix 用 ; 或 |
        'python -c "for i in range(5): print(i)" | '
        'python -c "import sys; print(sum(int(l) for l in sys.stdin))"',
        shell=True,
        capture_output=True,
        text=True,
    )
    print("  shell=True 结果:", r.stdout.strip())
    print("  只有最后进程的 returncode:", r.returncode)

    # Python 原生：稍繁琐但更可控
    p1 = subprocess.Popen(
        ["python", "-c", "for i in range(5): print(i)"],
        stdout=subprocess.PIPE, text=True,
    )
    p2 = subprocess.Popen(
        ["python", "-c",
         "import sys; print(sum(int(l) for l in sys.stdin))"],
        stdin=p1.stdout,
        stdout=subprocess.PIPE, text=True,
    )
    p1.stdout.close()
    out, _ = p2.communicate()
    p1.wait()
    print(f"  Python 原生结果: {out.strip()}，p1 returncode={p1.returncode}，p2 returncode={p2.returncode}")


if __name__ == "__main__":
    # demo01_two_process_pipe()
    # demo02_three_process_pipe()
    # demo03_deadlock_safe()
    demo04_shell_pipe_vs_python()
