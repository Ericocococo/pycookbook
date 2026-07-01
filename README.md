# pycookbook

> 一个存放 **Python 语法与实战代码**的配方集(cookbook)。
> 每个配方都尽量**可直接运行**:纯语法用 `.py` + `print` 展示结果,重环境的用 `.md` 笔记。

顶层按"知识的性质"分区,桶少而稳定;领域无限增长时往对应大区里加子目录,永远有明确落位。
完整设计思路见 [目录设计文档](STRUCTURE.md)。

---

## 快速开始

```bash
# 1) 克隆
git clone <repo-url> pycookbook
cd pycookbook

# 2) 建虚拟环境(推荐 Python 3.12)
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3) 安装核心工具链(ruff/mypy/pytest)
make install                     # 等价于 pip install -e ".[dev]"
```

领域依赖较重,**按需安装**,别默认全装:

```bash
pip install -e ".[libraries]"    # 04_libraries: httpx/pydantic/loguru...
pip install -e ".[backend]"      # 07_backend:   fastapi/sqlalchemy/redis...
pip install -e ".[data]"         # 08_data:      numpy/pandas/matplotlib...
pip install -e ".[ai]"           # 09_ai:        scikit-learn/transformers...
```

---

## 目录导航

| 区 | 内容 |
|----|------|
| [`01_language/`](01_language/) | 语言本身,basic → advanced → expert 递进 |
| [`02_algorithms/`](02_algorithms/) | 数据结构 / 经典算法 / 设计模式 |
| [`03_stdlib/`](03_stdlib/) | 常用标准库(查得最勤的那批) |
| [`04_libraries/`](04_libraries/) | pip 装完即用、跨领域的工具型库 |
| [`05_frameworks/`](05_frameworks/) | 开源应用框架/领域平台(vnpy 等),学架构 + 二次开发 |
| [`06_extending/`](06_extending/) | 扩展 Python / 高性能 / 跨语言(pybind11/cython/numba) |
| [`07_backend/`](07_backend/) | 后端工程: web/db/search/mq/rpc/api/auth/task/微服务 |
| [`08_data/`](08_data/) | 数据: 分析/可视化/工程/爬虫/存储 |
| [`09_ai/`](09_ai/) | AI: ml/dl/rl/推荐/nlp/cv/llm/agent/mlops |
| [`10_ops/`](10_ops/) | 工程化横切(纯工程活动): 测试/质量/打包/容器/CI/可观测/安全 |

> 目录一律带两位序号前缀(`01_ 02_ ...`),**阅读顺序即学习/工程顺序**。

---

## 怎么跑配方

```bash
# 纯语法配方 —— 直接执行,打印运行结果
python 01_language/01_basic/data_types.py

# 或用 pytest 批量跑(*_demo.py 也会被收集)
make test
```

---

## 常用命令

| 命令 | 作用 |
|------|------|
| `make install` | 安装核心开发工具链 |
| `make test` | 运行 pytest |
| `make lint` | ruff 检查风格与常见错误 |
| `make format` | ruff 自动格式化 |
| `make typecheck` | mypy 类型检查 |
| `make check` | 提交前一键跑 lint + typecheck + test |
| `make clean` | 清理缓存与构建产物 |

> Windows 上若没有 `make`,可直接敲对应原始命令(如 `pytest`、`ruff check .`),效果一样。

---

## 配方约定

1. **纯语法用可运行 `.py` + `print` 展示结果**;重框架/重环境的用 `.md` 笔记。
2. **文件顶部注释写清版本 + 安装命令** —— 三方库 API 变动大(如 pydantic v1→v2)。
3. **依赖统一锁在 `pyproject.toml`**,换机器一键装齐。
4. **所有层级目录带两位序号前缀**,顺序即导航。

更多细节见 [目录设计文档](STRUCTURE.md)。
