# sys —— Python 解释器接口与运行时信息

| 文件 | 内容 |
|------|------|
| `01_info.py` | 版本、平台、路径、数值限制等解释器静态信息 |
| `02_path_modules.py` | 模块搜索路径 sys.path、已加载模块缓存 sys.modules、import 机制钩子 |
| `03_io.py` | 标准流 stdin/stdout/stderr、编码查询、输出重定向 |
| `04_argv_exit.py` | 命令行参数解析、sys.exit 与 SystemExit 捕获、解释器启动标志 |
| `05_internals.py` | 引用计数、对象大小、递归深度、字符串驻留、异常信息 |

## 适用

- 在运行时检测 Python 版本、操作系统平台，做兼容性判断
- 动态操控模块搜索路径（临时添加路径而不修改环境变量）
- 重定向标准流，捕获函数内部的 print 输出（常用于测试）
- 获取命令行参数，以简单方式替代 argparse
- 调试引用计数、内存占用、递归错误等底层问题

## 不适用

- 复杂命令行解析（多子命令、类型校验、帮助文档）→ 用 argparse / click / typer
- 跨进程的标准流交互 → 用 subprocess.PIPE
- 生产级日志重定向 → 用 logging 模块（有处理器/格式器机制）
- 长期持久化的模块热重载 → 用 importlib.reload()

## 核心速查

```python
import sys

# 版本检测
sys.version_info >= (3, 10)          # 版本比较（推荐，比字符串比较可靠）
sys.platform                         # 'win32' / 'linux' / 'darwin'

# 路径操控
sys.path.insert(0, "/my/lib")        # 临时插入搜索路径（插到最前优先）

# 模块缓存
"json" in sys.modules                # 判断是否已加载
del sys.modules["json"]              # 清除缓存，下次 import 时重新加载

# 标准流重定向（捕获输出）
import io
buf = io.StringIO()
sys.stdout = buf
print("captured")
sys.stdout = sys.__stdout__          # 恢复原始流
result = buf.getvalue()              # "captured\n"

# 退出
sys.exit(0)                          # 正常退出（code=0）
sys.exit(1)                          # 异常退出（code≠0）
sys.exit("错误信息")                  # 打印到 stderr 后以 code=1 退出

# 引用计数与大小
sys.getrefcount(obj)                 # 对象引用计数（结果比实际多 1，因调用本身临时引用）
sys.getsizeof(obj)                   # 对象字节大小（浅层，不递归子对象）
```
