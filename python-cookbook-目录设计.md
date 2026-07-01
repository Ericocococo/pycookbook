# Python Cookbook 目录设计

> 一个存放 Python 语法与实战代码的仓库结构设计。
> 核心原则:**顶层按"知识的性质"分,桶少而稳定;领域无限增长时往对应大区里加子目录,永远有明确落位。**
> 约定:**所有层级目录统一带两位序号前缀(`01_ 02_ ...`),阅读顺序即学习/工程顺序。**

---

## 设计哲学

- **上半区 = "Python 怎么用"**(稳定、几乎不增长):`language / algorithms / stdlib / libraries / frameworks / extending`
- **下半区 = "用 Python 做什么"**(无限增长):`backend / data / ai / ops`
- 新东西来了,先问它属于哪个大区,再往里加子目录 —— 不会再出现"万能垃圾桶"。
- **不设计静态清单,而是设计生长规则。**
- **序号只表示顺序,不表示优先级**;插入新目录时就近取号,必要时整体重排。

---

## 顶层结构

```
pycookbook/
│
├── 01_language/      # 语言本身      —— 有限、稳定、几乎不增长
├── 02_algorithms/    # 算法与模式    —— ★新增:数据结构/经典算法/设计模式
├── 03_stdlib/        # 标准库        —— 有限
├── 04_libraries/     # 通用三方库    —— 缓慢增长(http/pydantic/loguru...)
├── 05_frameworks/    # 框架生态      —— 按框架加(fastapi/django...)
├── 06_extending/     # 扩展/性能     —— pybind11/cython/numba
│
├── 07_backend/       # ★ 后端工程    —— 无限增长区①
├── 08_data/          # ★ 数据        —— 无限增长区②
├── 09_ai/            # ★ 人工智能    —— 无限增长区③(最大)
└── 10_ops/           # ★ 工程化      —— 无限增长区④
```

---

## 完整目录树

```
pycookbook/                               # 顶层仓库(可运行的配方集)
│
├── README.md                             # 总索引:每个系列一句话导航
├── pyproject.toml                        # 依赖锁版本,一键装齐所有 demo 依赖
├── .python-version                       # 声明 Python 版本(如 3.12)
├── .gitignore                            # ★新增:忽略 __pycache__/.venv/*.egg-info 等
├── LICENSE                               # ★新增:开源许可证
├── Makefile                              # ★新增:make install/test/lint 常用入口
├── CONTRIBUTING.md                       # ★新增:配方风格与提交约定
├── .github/workflows/                    # ★新增:CI(装依赖→跑 assert→lint)
├── tests/                                # ★新增:全库集成/冒烟测试
│
├── 01_language/                          # ═══ 语言本身(按难度递进)═══
│   ├── 01_basic/                         # 基础
│   │   ├── data_types.py                     # 数值/字符串/bool
│   │   ├── containers.py                     # list/dict/set/tuple
│   │   ├── control_flow.py                   # if/for/while/match
│   │   ├── functions.py                      # 参数/返回值/作用域
│   │   ├── comprehensions.py                 # 推导式
│   │   ├── string_format.py                  # f-string/format
│   │   └── file_io.py                        # open/with/pathlib
│   ├── 02_advanced/                      # 高级
│   │   ├── oop.py                            # 类/继承/多态/魔术方法
│   │   ├── decorators.py                     # 装饰器
│   │   ├── generators_iterators.py           # 生成器/迭代器
│   │   ├── context_managers.py               # 上下文管理器
│   │   ├── exceptions.py                     # 异常/链式/异常组
│   │   ├── modules_packages.py               # 模块/包/import 机制
│   │   └── typing_hints.py                   # 类型注解
│   └── 03_expert/                        # 进阶(元编程/底层)
│       ├── metaclass.py                      # 元类
│       ├── descriptors.py                    # 描述符
│       ├── concurrency.py                    # 线程/进程/GIL
│       ├── asyncio_demo.py                   # 协程/异步
│       ├── memory_gc.py                      # 引用计数/垃圾回收
│       └── gotchas.py                        # 反直觉陷阱集
│
├── 02_algorithms/                        # ═══ ★新增:算法与设计模式 ═══
│   ├── 01_data_structures/               # 链表/栈/队列/树/图/堆/并查集
│   ├── 02_classic/                       # 排序/查找/递归分治/dp/贪心/回溯
│   └── 03_patterns/                      # 设计模式:单例/工厂/观察者/策略...
│
├── 03_stdlib/                            # ═══ 常用标准库(查得最勤)═══
│   ├── 01_collections_demo.py
│   ├── 02_itertools_functools.py
│   ├── 03_datetime_demo.py
│   ├── 04_json_pickle.py
│   ├── 05_re_regex.py
│   ├── 06_os_sys_subprocess.py
│   ├── 07_logging_demo.py
│   ├── 08_dataclasses_demo.py            # ★新增
│   ├── 09_enum_demo.py                   # ★新增
│   ├── 10_typing_demo.py                 # ★新增
│   ├── 11_contextlib_demo.py             # ★新增
│   ├── 12_argparse_demo.py               # ★新增
│   ├── 13_sqlite3_demo.py                # ★新增
│   ├── 14_hashlib_secrets.py             # ★新增
│   └── 15_concurrent_futures.py          # ★新增
│
├── 04_libraries/                         # ═══ 通用三方库(跨领域高频)═══
│   ├── 01_http/                              # requests/httpx/aiohttp
│   ├── 02_data_validation/                   # pydantic v2/marshmallow/attrs
│   ├── 03_serialization/                     # orjson/msgpack/protobuf
│   ├── 04_cli_tools/                         # click/typer/rich
│   ├── 05_config_log/                        # dotenv/dynaconf/loguru/structlog
│   ├── 06_datetime_util/                     # arrow/pendulum
│   ├── 07_retry_schedule/                    # tenacity/apscheduler
│   ├── 08_file_parse/                        # openpyxl/pyyaml/pillow/python-docx
│   ├── 09_crypto_auth/                       # pyjwt/passlib/cryptography
│   ├── 10_performance/                       # cachetools/line_profiler/memory_profiler
│   ├── 11_template/                      # ★新增:jinja2/mako 模板引擎
│   ├── 12_async_tools/                   # ★新增:anyio/trio 异步生态
│   └── 13_email_msg/                     # ★新增:email/smtplib/imap 收发信
│
├── 05_frameworks/                        # ═══ 框架 + 组件库生态(成系列)═══
│   │                                     #   统一三层: core → components → ecosystem
│   ├── 01_fastapi/
│   │   ├── 01_core/                          # routing/依赖注入/中间件
│   │   ├── 02_components/                    # pydantic/orm/认证/websocket
│   │   └── 03_ecosystem/                     # celery/alembic/testclient
│   ├── 02_django/
│   │   ├── 01_core/                          # orm/views/forms/admin
│   │   ├── 02_components/                    # DRF/django-filter/signals
│   │   └── 03_ecosystem/                     # celery/channels/cache/pytest-django
│   ├── 03_flask/
│   │   ├── 01_core/                          # 蓝图/上下文
│   │   └── 02_extensions/                    # sqlalchemy/migrate/login/jwt/marshmallow
│   ├── 04_scrapy/
│   │   ├── 01_core/                          # spider/items/selectors
│   │   └── 02_components/                    # pipeline/middlewares/scrapy-redis
│   ├── 05_sqlalchemy/
│   │   ├── 01_core/                          # engine/session/2.0 查询
│   │   └── 02_components/                    # relationship/alembic/async
│   └── 06_pydantic/
│       ├── models_validation.py
│       ├── settings_config.py
│       └── custom_validators.py
│
├── 06_extending/                         # ═══ 扩展 Python / 高性能 / 跨语言 ═══
│   ├── 01_ffi/                               # 调现成 C 库
│   │   ├── ctypes_demo.py
│   │   └── cffi_demo.py
│   ├── 02_native_ext/                        # 写扩展模块
│   │   ├── 01_pybind11/                      # ★ C++↔Python(含 cpp+cmake+README)
│   │   ├── 02_cython_demo/                   # .pyx 渐进加速
│   │   ├── 03_c_api/                         # 纯 CPython C-API
│   │   └── 04_nanobind/                      # pybind11 新一代替代
│   └── 03_speedup/                           # 纯 Python 提速
│       ├── numba_demo.py                     # JIT
│       ├── cython_pure.py
│       └── mypyc_notes.md
│
├── 07_backend/                           # ═══ ★ 后端工程 ═══
│   ├── 01_web/                               # fastapi/flask/django (框架细节在 05_frameworks/)
│   ├── 02_server/                            # socket/wsgi-asgi/部署
│   ├── 03_database/                          # sqlite/mysql/pg/redis/mongo/sqlalchemy
│   ├── 04_search/                        # ★新增:elasticsearch/opensearch/meilisearch
│   ├── 05_messaging/                         # ★ kafka / rabbitmq / redis-stream / pulsar
│   ├── 06_rpc/                               # ★ grpc / thrift / protobuf
│   ├── 07_api/                           # ★新增:REST/GraphQL/OpenAPI 规范与网关
│   ├── 08_auth/                          # ★新增:oauth2/jwt/session/rbac 认证鉴权
│   ├── 09_task_queue/                        # celery / apscheduler
│   └── 10_microservice/                      # 服务发现/网关/配置中心
│
├── 08_data/                              # ═══ ★ 数据 ═══
│   ├── 01_analysis/                          # numpy/pandas/polars
│   ├── 02_visualization/                 # ★新增:matplotlib/plotly/dash/pyecharts
│   ├── 03_engineering/                       # spark(pyspark)/dask/airflow/dbt 数据管道
│   ├── 04_spider/                            # requests+bs4/scrapy/playwright/反爬
│   └── 05_storage/                           # parquet/arrow/hdf5/时序库
│
├── 09_ai/                                # ═══ ★★ 人工智能(体量最大,独立成世界)═══
│   ├── 01_ml/                                # 机器学习: sklearn/xgboost/lightgbm/特征工程
│   ├── 02_dl/                                # 深度学习: pytorch/tensorflow/训练循环/分布式
│   ├── 03_rl/                            # ★新增:强化学习: gymnasium/stable-baselines3
│   ├── 04_recommend/                     # ★新增:推荐系统: 召回/排序/embedding 检索
│   ├── 05_nlp/                               # 自然语言: transformers/tokenizer/jieba/nltk
│   ├── 06_cv/                                # 计算机视觉: opencv/torchvision/目标检测/分割
│   ├── 07_llm/                               # ★ 大模型: openai/anthropic-api/prompt/RAG/embedding/向量库
│   ├── 08_agent/                             # ★ 智能体: langgraph/autogen/tool-calling/MCP/多智能体
│   ├── 09_audio_speech/                      # 语音: whisper/tts/asr
│   └── 10_mlops/                             # 模型工程: mlflow/onnx/triton/模型部署与量化
│
└── 10_ops/                               # ═══ ★ 工程化(横切所有领域)═══
    ├── 01_testing/                           # pytest/mock/hypothesis
    ├── 02_lint_format/                   # ★新增:ruff/black/mypy/pre-commit 代码质量
    ├── 03_packaging/                         # uv/poetry/pyproject/打包发布
    ├── 04_cli/                               # click/typer/rich
    ├── 05_config_log/                        # dotenv/pydantic-settings/loguru
    ├── 06_container/                         # docker/k8s 相关 python 工具
    ├── 07_ci_cd/                             # 自动化脚本
    └── 08_observability/                     # 日志/指标/tracing (opentelemetry)
```

---

## 根级文件说明

顶层那几个"非配方"文件各司其职,合起来让仓库能一键装、一键测、一键检查:

| 文件 / 目录 | 作用 | 说明 |
|-------------|------|------|
| `README.md` | 总索引 | 每个系列一句话导航,新人从这进 |
| `pyproject.toml` | **项目配置中心** | 三合一:①项目元数据 ②依赖清单(`pip install -e .` 一键装)③工具配置(ruff/mypy/pytest 规则都写这)。**不绑定构建语言** |
| `.python-version` | 声明 Python 版本 | pyenv 等据此自动切版本(本仓库 3.12) |
| `.gitignore` | git 忽略清单 | 缓存、`.venv`、`.env` 密钥、编译产物、AI/数据大文件都不进版本库 |
| `LICENSE` | 开源许可证 | 声明代码使用授权 |
| `Makefile` | **命令快捷方式表** | 把长命令起短名:`make test`=`pytest`,`make lint`=`ruff check .`。**只是通用命令运行器,不认语言、不写 C** |
| `CONTRIBUTING.md` | 贡献约定 | 配方风格与提交规范 |
| `.github/workflows/` | CI | 推代码时自动装依赖→跑 assert→lint |
| `tests/` | 全库集成/冒烟测试 | 跨配方的整体验证 |

> **关于 `CMakeLists.txt`**:它和 `Makefile` 名字像,但**强绑定 C/C++**——是把 C++ 源码编译成可执行文件/动态库的构建配置。本仓库只有 `06_extending/02_native_ext/01_pybind11/` 用 C++ 写 Python 扩展时才会出现它;纯 Python 配方一律不需要。

---

## 十大区速记

| 区 | 性质 | 一句话 |
|----|------|--------|
| `01_language` | 稳定 | 语法本身,basic→advanced→expert 递进 |
| `02_algorithms` | 稳定 | ★数据结构/经典算法/设计模式 |
| `03_stdlib` | 稳定 | 装机自带、查得最勤的那批 |
| `04_libraries` | 缓慢增长 | pip 装完即用、跨领域的工具型库 |
| `05_frameworks` | 按框架加 | 以框架为轴,core→components→ecosystem |
| `06_extending` | 稳定 | 太慢/复用 C++ 怎么办,选型光谱 |
| `07_backend` | 无限增长 | 后端工程: web/db/search/mq/rpc/api/auth/task/微服务 |
| `08_data` | 无限增长 | 数据: 分析/可视化/工程/爬虫/存储 |
| `09_ai` | 无限增长 | AI 大世界: ml/dl/rl/推荐/nlp/cv/llm/agent/mlops |
| `10_ops` | 无限增长 | 工程化横切: 测试/质量/打包/CI/可观测 |

---

## 贯穿全库的约定

1. **纯语法用可运行 `.py` + `assert` 自验**;重框架/重环境的用 `.md` 笔记(Django、pybind11、部署)。
2. **文件顶部注释写清版本 + 安装命令** —— 三方库 API 变动大(如 pydantic v1→v2 破坏性升级)。
3. **依赖统一锁在 `pyproject.toml`** —— 换机器一键 `pip install -e .` 装齐。
4. **所有层级目录统一带两位序号前缀** `01_ 02_ ...` —— 顺序即导航;插入新目录就近取号,幅度大就整体重排。工程约定目录(`tests/`、`.github/`)按惯例不加号。
5. **别把顶层命名为 `python` 或 `test`** —— 会和解释器概念、pytest/标准库 `test` 模块混淆。

---

## 扩展策略(体量失控时)

当 `09_ai/` 将来自己就长到几百个文件、依赖(torch/cuda 几个 G)重到拖累纯语法 demo 时 —— **拆成多仓库(polyrepo)**:

- `pycookbook` → 只留 `language/algorithms/stdlib/libraries/frameworks/extending`(**稳定核心**)
- `ai-cookbook`、`backend-cookbook` → 各自独立 repo,独立依赖、独立 CI

**依赖差异大到互相拖累时,就是该拆仓的信号。**
