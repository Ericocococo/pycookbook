# 性能分析（Profiling）

定位 Python 程序慢在哪里：函数级 → 行级 → 可视化。

| 文件 | 内容 |
|------|------|
| [01_cprofile.py](01_cprofile.py) | cProfile + pstats：字段说明、run/Profile对象/context manager、过滤、调用关系、保存合并、与 timeit 对比 |

## 工具选型

```text
工具             类型       适合场景
-----------      -------    ----------------------------
cProfile         标准库     整体分析，找慢在哪个函数（入门首选）
pstats           标准库     读取 cProfile 结果并格式化（配套使用）
timeit           标准库     精确测量单个表达式
line_profiler    第三方     行级分析，cProfile 定位后再细看
memory_profiler  第三方     内存占用分析
snakeviz         第三方     .prof 文件可视化（火焰图）
py-spy           第三方     生产环境采样，零侵入
```

## 典型工作流

```bash
# 1. 先用 cProfile 找到慢函数
python -m cProfile -o result.prof script.py

# 2. 可视化确认调用链
snakeviz result.prof

# 3. 对慢函数做行级分析（需安装 line_profiler）
pip install line-profiler
kernprof -l -v script.py   # 在函数上加 @profile 装饰器
```

## 输出字段速查

```text
ncalls   调用次数
tottime  自身耗时（不含子函数）← 找真正热点
cumtime  含子函数的累计耗时   ← 找慢调用链
```

## 安装

```bash
pip install snakeviz        # 可视化（强烈推荐）
pip install line-profiler   # 行级分析
```
