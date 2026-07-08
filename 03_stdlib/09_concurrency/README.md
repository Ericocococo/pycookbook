# 并发：线程 / 进程 / 协程

| 目录 | 模块 | 内容 |
|------|------|------|
| [01_threading/](01_threading/) | `threading` | Thread / Lock / Event / Condition / Queue |
| [02_multiprocessing/](02_multiprocessing/) | `multiprocessing` | Process / Pool / Queue / Pipe / 共享内存 |
| [03_asyncio/](03_asyncio/) | `asyncio` | 协程 / Task / gather / Queue / 异步 IO |
| [04_futures/](04_futures/) | `concurrent.futures` | ThreadPoolExecutor / ProcessPoolExecutor / as_completed |

## 选型指南

```
任务类型？
├── IO 密集（网络请求、文件读写、数据库）
│   ├── 需要高并发（成千上万连接）→ asyncio（协程）
│   └── 并发量一般（几十个）      → threading 或 futures.ThreadPool
└── CPU 密集（数值计算、图像处理、加密）
    → multiprocessing 或 futures.ProcessPool
    （多线程在 CPU 密集场景因 GIL 无法真正并行，没有加速效果）
```

## 核心概念

| 术语 | 含义 |
|------|------|
| **GIL** | 全局解释器锁，同一时刻只有一个线程执行 Python 字节码；IO 等待时自动释放，CPU 密集场景下多线程无法并行 |
| **进程** | 操作系统资源隔离单元，有独立内存空间；进程间通信需要 Queue / Pipe |
| **线程** | 进程内共享内存的执行单元；共享数据需要 Lock 保护 |
| **协程** | 用户态切换，单线程内并发，通过 `await` 主动让出控制权；不受 GIL 限制 IO |
| **竞态条件** | 多线程同时读写共享变量，结果依赖执行顺序，产生不可预期的错误 |
| **死锁** | 两个线程互相等待对方释放锁，双方都无法继续 |

## 各方案对比

| | threading | multiprocessing | asyncio | concurrent.futures |
|---|---|---|---|---|
| 适合场景 | IO 密集 | CPU 密集 | 高并发 IO | 两者简化封装 |
| 内存 | 共享 | 独立（复制） | 共享 | 取决于 Pool 类型 |
| GIL 影响 | 受限 | 不受限 | 不受限 IO | 取决于 Pool 类型 |
| 通信方式 | 共享变量 + Lock | Queue / Pipe | await / Queue | Future 对象 |
| 启动开销 | 小 | 大 | 极小 | 中等 |
| 代码复杂度 | 中 | 中 | 较高 | 低（推荐入门） |
