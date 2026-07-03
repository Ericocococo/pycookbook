# importlib —— 动态导入与包工具

| 文件 | 内容 |
|------|------|
| [01_import_module.py](01_import_module.py) | `import_module` 动态导入 / `reload` 热重载 / 与 `__import__` 对比 |
| [02_util.py](02_util.py) | `find_spec` 检查模块是否存在 / `spec_from_file_location` 从任意路径加载 .py |
| [03_metadata.py](03_metadata.py) | `importlib.metadata`：读取已安装包的版本 / 依赖 / 入口点 |
| [04_resources.py](04_resources.py) | `importlib.resources`：读取包内嵌资源文件（数据文件 / 文本 / 二进制） |

## 核心概念

| 术语 | 含义 |
|------|------|
| **模块规格（ModuleSpec）** | 描述如何找到并加载一个模块的元数据对象（路径、loader 等） |
| **loader** | 实际执行加载（读取文件、编译、执行）的对象，挂在 ModuleSpec 上 |
| **sys.modules** | 已导入模块的缓存字典，`import` 时先查这里；`reload` 会绕过缓存 |
| **入口点（entry_points）** | 包在安装时注册的钩子，让其他工具发现并调用它（如 CLI 命令、插件） |

## 适用

- 运行时根据配置/用户输入动态导入模块（插件系统）
- 检查某个模块或第三方包是否已安装
- 从任意路径加载 .py 文件（不放入 sys.path）
- 读取已安装包的版本号、依赖列表
- 访问打包进 wheel 的数据文件（不依赖 `__file__` 路径拼接）

## 不适用

- 普通的静态导入 → 直接 `import`
- 自定义 import 机制（finder / loader）→ `importlib.abc`（底层 API，极少用）

## 核心速查

```python
import importlib
import importlib.util
import importlib.metadata

# 动态导入（等价于 import json）
json = importlib.import_module("json")

# 检查模块是否存在（不导入）
spec = importlib.util.find_spec("numpy")
print("numpy 已安装:", spec is not None)

# 从任意路径加载 .py 文件
spec = importlib.util.spec_from_file_location("mymod", "/path/to/plugin.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# 查询已安装包版本
print(importlib.metadata.version("pip"))
```
