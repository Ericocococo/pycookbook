# Pyright —— 高性能 Python 静态类型检查器

> 微软出品的**静态类型检查**工具，用 TypeScript 编写，比 Mypy 快数倍到数十倍。
> VS Code Pylance 的内核就是 Pyright，大量 VS Code 用户每天在用但未必知道。

## 1. 文件说明

| 文件 | 内容 | 运行方式 |
|------|------|----------|
| [01_config.py](01_config.py) | Pyright 配置与检查等级 | `pyright 01_config.py` |
| [02_stub.py](02_stub.py) | .pyi 桩文件、typeshed、--verifytypes | `pyright 02_stub.py` |
| [03_step_by_step/](03_step_by_step/) | LSP 协议从零拆解（管道→消息→初始化→补全→WebSocket→桥接） | 按目录内序号逐个运行 |
| [04_monaco_lsp/](04_monaco_lsp/) | Monaco Editor + LSP bridge 前端集成 | `cd 04_monaco_lsp && python 01_http_server.py --serve` |
| [05_enterprise.md](05_enterprise.md) | 企业级：CI/CD、增量接入、Monorepo、性能调优 | 直接阅读 |
| [pyrightconfig.json](pyrightconfig.json) | 项目级 Pyright 配置 | 自动生效 |

## 2. 适用 / 不适用

| 场景 | 推荐 |
|------|------|
| **大型项目初次接入类型检查** | ✅ Pyright（增量、按文件配置，无需改完所有错误） |
| **VS Code 用户** | ✅ Pylance 已内置，开箱即用 |
| **CI 中做类型检查** | ✅ `pyright` CLI 无头运行，比 Mypy 快 |
| **已有 Mypy 的项目想互补** | ✅ 两者可共存，Pyright 有时能查出 Mypy 遗漏的 bug |
| **需要严格纯 Python 类型检查** | ⚠️ Mypy 对某些边缘场景更严谨（如 `__init__` 返回值检查） |
| **Python 2 项目** | ❌ Pyright 仅支持 Python 3 |

## 3. 核心概念

### Pyright 是什么

- **类型检查器**：不运行代码，只分析源码中的类型注解和变量传递路径，发现类型不匹配
- **与 Mypy 的关系**：功能等价，但实现完全不同

| 对比维度 | Pyright | Mypy |
|---------|---------|------|
| 实现语言 | TypeScript | Python |
| 检查速度 | 快（增量 + 多核并行） | 较慢 |
| VS Code 集成 | Pylance 内置 | 需安装插件 |
| 配置方式 | `pyrightconfig.json` / `pyproject.toml` | `mypy.ini` / `pyproject.toml` |
| 对三方库 stubs | 内置 stub 仓库 | 同样支持 |
| 严格模式 | `typeCheckingMode: "strict"` | `--strict` |

### 核心能力速览

```python
# ① 类型推断 —— 自动推导变量类型，无需注解
x = 42         # int
y = "hello"    # str
z = [1, 2, 3]  # list[int]

# ② 类型注解 —— 显式声明，人类和检查器都能看懂
def greet(name: str) -> str:
    return f"Hello, {name}"

# ③ 类型收窄 —— 类型守卫让联合类型变精确
def process(val: int | str) -> str:
    if isinstance(val, int):
        # 此处 val 被收窄为 int
        return str(val * 2)
    # 此处 val 被收窄为 str
    return val.upper()
```

## 4. 安装

```bash
# 全局安装（推荐，所有项目共用）
npm install -g pyright

# 验证安装
pyright --version
# → pyright 1.1.xxx

# 项目级安装（锁定版本）
npm install --save-dev pyright
npx pyright --version

# pip 安装（社区维护的封装，体验次之）
pip install pyright
```

## 5. 基础用法

```bash
# 检查整个项目（自动读取 pyrightconfig.json）
pyright

# 检查单个文件
pyright path/to/file.py

# 检查多个文件
pyright src/main.py src/utils.py

# 只看错误，不显示信息/警告
pyright --level error

# 输出 JSON 格式（CI 或工具集成用）
pyright --outputjson
```

## 6. 配置文件

Pyright 从**项目根目录**向下查找配置，按优先级：`pyrightconfig.json` > `pyproject.toml`（`[tool.pyright]` 段）。

核心配置项：

| 配置项 | 作用 |
|--------|------|
| `typeCheckingMode` | `"off"` / `"basic"`（默认）/ `"strict"` |
| `include` | 要检查的文件/目录，支持 glob |
| `exclude` | 排除的文件/目录 |
| `pythonVersion` | 目标 Python 版本 |
| `pythonPlatform` | `"Linux"` / `"Darwin"` / `"Windows"` |
| `venvPath` | 虚拟环境根目录 |
| `reportXxx` | 200+ 细粒度开关，控制每类检查的报错级别 |

## 7. 检查等级体系

Pyright 有三层控制粒度：

```
全局模式         细粒度开关             行内注释
─────────       ────────────           ────────
basic            reportXxx=none        # pyright: ignore
strict           reportXxx=warning
                 reportXxx=error
                 reportXxx=information
```

### 行内忽略

```python
x: int = "hello"  # pyright: ignore

# 指定规则名（推荐，避免误吞真正的问题）
y: int = "hello"  # pyright: ignore[reportAssignmentType]

# 当前行 + 下一行
# pyright: off
z: int = "not int"
z = 42
# pyright: on
```

## 8. 常见场景

### 8.1 增量接入旧项目

```json
{
  "typeCheckingMode": "basic",
  "include": ["src"],
  "exclude": ["src/legacy/**"],
  "reportOptionalMemberAccess": "warning"
}
```

先设为 `"basic"` 只看明显错误，再逐目录提到 `"strict"`。

### 8.2 与 Mypy 共存

```json
{
  "typeCheckingMode": "basic",
  "reportMissingTypeStubs": "information",
  "reportUnknownMemberType": "none"
}
```

Mypy 走的是另一套配置，两者互不干扰。同一个 CI 里可以先跑 Pyright（快），再跑 Mypy（全）。

### 8.3 在 CI 中使用

```bash
# GitHub Actions / GitLab CI
pyright --outputjson | jq -e '.summary.errorCount == 0'
```

## 9. 进阶类型特性

### 9.1 TypeGuard —— 自定义类型守卫

[05_type_guards.py](05_type_guards.py) 详细演示。

```python
from typing import TypeGuard

def is_str(val: object) -> TypeGuard[str]:
    return isinstance(val, str)

values: list[object] = ["hello", 42]
for v in values:
    if is_str(v):
        # 此处 v 被收窄为 str
        print(v.upper())
```

### 9.2 TypeIs（Python 3.13+）

与 TypeGuard 类似，但 True/False 双向收窄：

```python
from typing import TypeIs

def is_dog(animal: object) -> TypeIs[Dog]:
    return isinstance(animal, Dog)

if is_dog(pet):
    pet.bark()  # 收窄为 Dog
else:
    pet.meow()  # 排除 Dog，剩下 Cat
```

### 9.3 @overload —— 函数重载

同一个函数名，根据参数类型返回不同类型：

```python
from typing import overload

@overload
def double(value: int) -> int: ...
@overload
def double(value: str) -> str: ...

def double(value: int | str) -> int | str:
    if isinstance(value, int):
        return value * 2
    return value * 2
```

### 9.4 递归类型别名

```python
from typing import TypeAlias

JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None
```

## 10. 类型 Stub 管理

[02_stub.py](02_stub.py) 详细演示。

### 10.1 .pyi 桩文件

`mylib.pyi` —— 只有类型声明，没有实现体：

```python
def connect(host: str, port: int = 8080) -> Connection: ...
class Connection:
    def send(self, data: bytes) -> None: ...
```

适用：C 扩展库、不想改源码的三方库、API 类型约束。

### 10.2 typeshed

Pyright 内置社区维护的 [typeshed](https://github.com/python/typeshed) 仓库，
标准库和流行三方库的类型开箱即用。

### 10.3 --verifytypes 类型完整度

```bash
pyright --verifytypes mypackage
# → Type completeness score: 96.7%
```

检查包的公共 API 是否都有类型注解，库作者保证类型质量的重要工具。

### 10.4 stubPath

```json
{ "stubPath": "typings" }
```

`typings/some_package.pyi` 覆盖某库的类型。

### 10.5 deprecateTypingAliases

```json
{ "deprecateTypingAliases": true }
```

Python 3.9+ 推荐用 `list[int]` 而非 `typing.List[int]`，
开启后使用旧别名会报 warning。

## 11. 企业级实践

详见 [05_enterprise.md](05_enterprise.md)，覆盖：

| 场景 | 关键内容 |
|------|---------|
| **CI/CD 集成** | GitHub Actions、GitLab CI、pre-commit、增量 CI |
| **大型项目增量接入** | 四阶段方案、executionEnvironments 逐目录渗透 |
| **Monorepo 配置** | 多包独立配置、共享类型、extraPaths |
| **性能调优** | exclude、多线程、stats 诊断、缓存 |
| **Pyright + Mypy 双检** | 双检 CI 配置、各自优势互补 |

## 12. 与其他工具的关系

```
ruff        ← 代码格式 + 简单 lint（不检查类型）
mypy        ← 纯 Python 实现的类型检查器
pyright     ← TypeScript 实现的类型检查器，Pylance 内核
pylance     ← VS Code 扩展，UI + 补全 + Pyright 类型检查
```

Ruff 管格式、Mypy/Pyright 管类型——**互补而非竞争**。

## 参考资料

- [Pyright 官方文档](https://microsoft.github.io/pyright/)
- [Pyright GitHub](https://github.com/microsoft/pyright)
- [Pyright 配置参考](https://microsoft.github.io/pyright/#/configuration)
