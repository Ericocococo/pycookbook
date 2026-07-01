# Python Cookbook 目录设计

> 一个存放 Python 语法与实战代码的仓库结构设计。
> 核心原则:**顶层按"知识的性质"分,桶少而稳定;领域无限增长时往对应大区里加子目录,永远有明确落位。**
> 约定:**所有层级目录统一带两位序号前缀(`01_ 02_ ...`),阅读顺序即学习/工程顺序。**

---

## 设计哲学

- **上半区(01–06,"Python 怎么用")**:`language / algorithms / stdlib / libraries / extending` 大多稳定、几乎不增长;
  唯 `05_frameworks`(开源应用框架 vnpy/godzilla…)是例外 —— 它随所研究的项目增长、依赖偏重,只是序号恰好排在此处。
- **下半区(07–10,"用 Python 做什么")**(无限增长):`backend / data / ai / ops`
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
├── 05_frameworks/    # 开源应用框架  —— 领域平台/开源系统二开(vnpy/godzilla...)
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
├── .github/workflows/                    # ★新增:CI(装依赖→跑测试→lint)
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
│   │                                     #   每个库一个子目录,内部按功能拆成多个带序号 .py;
│   │                                     #   紧密相关的小库可合并一个目录(如 json_pickle、os_sys_subprocess)
│   ├── 01_argparse/                      # 命令行解析: basic/types/actions/nargs/groups/subcommands/help/advanced
│   ├── 02_collections/                   # namedtuple/deque/Counter/defaultdict/OrderedDict
│   ├── 03_itertools_functools/           # 迭代器工具 + 高阶函数/lru_cache/partial
│   ├── 04_datetime/                      # date/time/datetime/timedelta/时区
│   ├── 05_json_pickle/                   # json 序列化 / pickle 对象持久化
│   ├── 06_re_regex/                      # 正则: match/search/findall/sub/分组
│   ├── 07_os_sys_subprocess/             # 路径/环境变量/进程调用
│   ├── 08_logging/                       # logger/handler/formatter/级别
│   ├── 09_dataclasses/                   # ★新增: @dataclass/field/post_init
│   ├── 10_enum/                          # ★新增: Enum/IntEnum/auto/Flag
│   ├── 11_typing/                        # ★新增: 泛型/Protocol/TypedDict/Union
│   ├── 12_contextlib/                    # ★新增: contextmanager/suppress/ExitStack
│   ├── 13_sqlite3/                       # ★新增: 连接/游标/事务/参数化查询
│   ├── 14_hashlib_secrets/               # ★新增: 哈希/摘要/安全随机
│   └── 15_concurrent_futures/            # ★新增: ThreadPool/ProcessPool/Executor
│
├── 04_libraries/                         # ═══ 通用三方库(跨领域高频)═══
│   ├── 01_http/                              # requests/httpx/aiohttp
│   ├── 02_data_validation/                   # pydantic v2/marshmallow/attrs
│   ├── 03_serialization/                     # orjson/msgpack/protobuf(protobuf 主位;RPC 用法见 07_backend/06_rpc)
│   ├── 04_cli_tools/                         # click/typer/rich
│   ├── 05_config_log/                        # dotenv/dynaconf/loguru/structlog
│   ├── 06_datetime_util/                     # arrow/pendulum
│   ├── 07_retry_schedule/                    # tenacity/apscheduler(库用法主位;任务队列见 07_backend/09)
│   ├── 08_file_parse/                        # openpyxl/pyyaml/pillow/python-docx
│   ├── 09_crypto_auth/                       # pyjwt/passlib/cryptography(jwt 库主位;鉴权流程见 07_backend/08)
│   ├── 10_performance/                       # cachetools/line_profiler/memory_profiler
│   ├── 11_template/                      # ★新增:jinja2/mako 模板引擎
│   ├── 12_async_tools/                   # ★新增:anyio/trio 异步生态
│   └── 13_email_msg/                     # ★新增:email/smtplib/imap 收发信
│
├── 05_frameworks/                        # ═══ 开源应用框架(领域平台,在其之上二次开发)═══
│   │                                     #   ★重定义:这里不是通用 web 框架 —— fastapi/django/
│   │                                     #   flask 已迁到 07_backend/01_web/;sqlalchemy→database、
│   │                                     #   scrapy→08_data/04_spider、pydantic→04_libraries。
│   │                                     #   本区专放 vnpy/godzilla 这类完整的领域级开源系统:
│   │                                     #   学它的架构、怎么用、怎么二次开发。
│   │                                     #   组织:领域 → 具体框架 → 架构笔记/使用/二开示例
│   └── 01_quant/                         # 量化交易
│       ├── 01_vnpy/                          # vnpy 量化交易系统框架(架构/策略开发/回测/二开)
│       └── 02_godzilla/                      # godzilla-community 量化框架(待调研)
│                                         #   其他领域/框架用到再按 NN_领域/NN_框架 追加
│
├── 06_extending/                         # ═══ 扩展 Python / 高性能 / 跨语言 ═══
│   ├── 01_ffi/                               # 调现成 C 库
│   │   ├── 01_ctypes/                            # ctypes
│   │   └── 02_cffi/                              # cffi
│   ├── 02_native_ext/                        # 写扩展模块
│   │   ├── 01_pybind11/                      # ★ C++↔Python(含 cpp+cmake+README)
│   │   ├── 02_cython_demo/                   # .pyx 渐进加速
│   │   ├── 03_c_api/                         # 纯 CPython C-API
│   │   └── 04_nanobind/                      # pybind11 新一代替代
│   └── 03_speedup/                           # 纯 Python 提速
│       ├── 01_numba/                            # JIT
│       ├── 02_cython_pure/                      # 纯 .py 加 cython 类型
│       └── 03_mypyc/                            # mypyc 笔记
│
├── 07_backend/                           # ═══ ★ 后端工程 ═══
│   ├── 01_web/                              # ★通用 web 框架都在这(从 05_frameworks 迁入)
│   │   ├── 01_fastapi/                       # 01_core / 02_components / 03_ecosystem
│   │   ├── 02_django/                        # 01_core / 02_components(DRF) / 03_ecosystem
│   │   └── 03_flask/                         # 01_core / 02_extensions
│   ├── 02_server/                            # socket/wsgi-asgi/部署
│   ├── 03_database/                          # sqlite/mysql/pg/redis/mongo/sqlalchemy
│   ├── 04_search/                        # ★新增:elasticsearch/opensearch/meilisearch
│   ├── 05_messaging/                         # ★ kafka / rabbitmq / redis-stream / pulsar
│   ├── 06_rpc/                               # ★ grpc/thrift(protobuf 序列化见 04_libraries/03)
│   ├── 07_api/                           # ★新增:REST/GraphQL/OpenAPI 规范 + API 网关(网关归这)
│   ├── 08_auth/                          # ★新增:oauth2/session/rbac 鉴权流程(jwt 库见 04_libraries/09)
│   ├── 09_task_queue/                        # celery 分布式任务(apscheduler 库用法见 04_libraries/07)
│   └── 10_microservice/                      # 服务发现/服务网格/配置中心(API 网关见 07_api)
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
└── 10_ops/                               # ═══ ★ 工程化(横切;只放"纯工程活动",不放库用法)═══
    ├── 01_testing/                           # pytest/mock/hypothesis
    ├── 02_lint_format/                       # ruff/black/mypy/pre-commit 代码质量
    ├── 03_packaging/                         # uv/poetry/pyproject/打包发布
    ├── 04_container/                         # docker/k8s 相关 python 工具
    ├── 05_ci_cd/                             # 自动化脚本
    ├── 06_observability/                     # 日志/指标/tracing (opentelemetry)
    └── 07_security/                          # ★新增:bandit/safety 依赖扫描/密钥检测
    # 注:cli / config_log 属"库用法",统一在 04_libraries,ops 不重复(见约定 6)
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
| `.github/workflows/` | CI | 推代码时自动装依赖→跑测试→lint |
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
| `05_frameworks` | 按领域增长 | ★开源应用框架/领域平台(vnpy 等),学架构 + 二开;通用 web 框架在 backend |
| `06_extending` | 稳定 | 太慢/复用 C++ 怎么办,选型光谱 |
| `07_backend` | 无限增长 | 后端工程: web/db/search/mq/rpc/api/auth/task/微服务 |
| `08_data` | 无限增长 | 数据: 分析/可视化/工程/爬虫/存储 |
| `09_ai` | 无限增长 | AI 大世界: ml/dl/rl/推荐/nlp/cv/llm/agent/mlops |
| `10_ops` | 无限增长 | 工程化横切(纯工程活动): 测试/质量/打包/容器/CI/可观测/安全 |

---

## 贯穿全库的约定

1. **纯语法用可运行 `.py` + `print` 展示结果**;重框架/重环境的用 `.md` 笔记(Django、pybind11、部署)。
2. **文件顶部注释写清版本 + 安装命令** —— 三方库 API 变动大(如 pydantic v1→v2 破坏性升级)。
3. **依赖统一锁在 `pyproject.toml`** —— 换机器一键 `pip install -e .` 装齐。
4. **所有层级目录统一带两位序号前缀** `01_ 02_ ...` —— 顺序即导航;插入新目录就近取号,幅度大就整体重排。工程约定目录(`tests/`、`.github/`)按惯例不加号。
5. **别把顶层命名为 `python` 或 `test`** —— 会和解释器概念、pytest/标准库 `test` 模块混淆。
6. **`04_libraries` 与 `10_ops` 分工** —— "某个库怎么用"(含 cli/config/log 等工具库)归 `04_libraries`;
   "纯工程活动/流程"(测试/代码质量/打包/容器/CI/可观测)归 `10_ops`,两边不重复。

---

## 扩展策略(体量失控时)

当 `09_ai/` 将来自己就长到几百个文件、依赖(torch/cuda 几个 G)重到拖累纯语法 demo 时 —— **拆成多仓库(polyrepo)**:

- `pycookbook` → 只留 `language/algorithms/stdlib/libraries/extending`(**稳定核心**)
- `ai-cookbook`、`backend-cookbook`、`frameworks`(vnpy 等重框架)→ 各自独立 repo,独立依赖、独立 CI

**依赖差异大到互相拖累时,就是该拆仓的信号。**
