# subprocess —— 启动和管理子进程

| 文件 | 内容 |
|------|------|
| [01_run.py](01_run.py) | `subprocess.run`：基础调用 / 捕获输出 / check / cwd / env / timeout |
| [02_output.py](02_output.py) | 输出控制：PIPE / DEVNULL / 合并 stderr / 编码 / 实时流读取 |
| [03_popen.py](03_popen.py) | `Popen`：逐行读取 / communicate / stdin 交互 / poll / wait |
| [04_pipe.py](04_pipe.py) | 管道链：Python 原生替代 `cmd1 \| cmd2` / 死锁陷阱 |
| [05_advanced.py](05_advanced.py) | 进阶：超时清理 / 后台进程 / shell 注入陷阱 / Windows 无窗口运行 |

## 核心概念

| 术语 | 含义 |
|------|------|
| **子进程** | 由当前 Python 进程（父进程）启动的独立操作系统进程 |
| **returncode** | 子进程退出码，0 = 成功，非 0 = 出错（Unix 约定） |
| **PIPE** | `subprocess.PIPE`，让父进程通过内存管道读写子进程的 stdin/stdout/stderr |
| **DEVNULL** | `subprocess.DEVNULL`，把输出扔进黑洞（类似重定向到 `/dev/null`） |
| **communicate()** | 一次性发完 stdin、读完 stdout/stderr，自动避免死锁，推荐优先用 |
| **shell=True** | 通过系统 shell（cmd / bash）执行命令字符串，方便但有命令注入风险 |

## 适用

- 调用系统命令（`git`、`ffmpeg`、`ping`…）并获取输出
- 启动外部程序并与其交互（发送输入、读取实时输出）
- 串联多个命令（替代 shell 管道）

## 不适用

- 只需要运行简单命令且不关心输出 → `os.system()` 够用（但不推荐）
- 需要在同一进程内并发 → `threading` / `asyncio`
- 需要跨机器执行 → `paramiko`（SSH）

## 核心速查

```python
import subprocess

# 最常用：run + 捕获输出 + 自动解码 + 出错抛异常
r = subprocess.run(["git", "log", "--oneline", "-5"],
                   capture_output=True, text=True, check=True)
print(r.stdout)          # 标准输出字符串
print(r.returncode)      # 0

# 不捕获，直接打印到终端
subprocess.run(["ls", "-l"])

# 需要实时读取输出时用 Popen
with subprocess.Popen(["ping", "127.0.0.1", "-n", "3"],
                      stdout=subprocess.PIPE, text=True) as p:
    for line in p.stdout:
        print(line, end="")
```
