"""cProfile + pstats 性能分析

依赖: pip install snakeviz   （可视化，可选）
Python 3.12。运行: python 01_cprofile.py

cProfile  — 采集器：统计每个函数的调用次数和耗时
pstats    — 报表工具：读取 cProfile 结果并格式化输出
两者配套使用，cProfile 采集，pstats 呈现。

命令行用法：
    python -m cProfile -s cumtime script.py        # 按累计时间排序
    python -m cProfile -s tottime script.py        # 按自身时间排序
    python -m cProfile -o result.prof script.py    # 输出到文件
    snakeviz result.prof                           # 浏览器可视化火焰图
"""
import cProfile
import io
import pathlib
import pstats
import sys

DATA_DIR = pathlib.Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# 被分析的示例代码（故意制造慢点）
# ---------------------------------------------------------------------------

def slow_io(n=200_000):
    result = ""
    for i in range(n):
        result += str(i)
    return result


def fast_io(n=200_000):
    return "".join(str(i) for i in range(n))


def compute(n=500):
    total = 0
    for i in range(n):
        for j in range(n):
            total += i * j
    return total


def main_workflow():
    slow_io()
    fast_io()
    compute()


# ---------------------------------------------------------------------------
# ① 读懂输出字段（先看，再跑）
# ---------------------------------------------------------------------------

def demo01_explain():
    """① 输出字段说明 + 真实示例对照"""
    print("① 输出字段说明")

    # 先跑一次，拿到真实输出
    # 等价写法：
    #   pr = cProfile.Profile()
    #   pr.enable()
    #   main_workflow()
    #   pr.disable()
    with cProfile.Profile() as pr:  # 进入时 enable()，退出时自动 disable()；as pr 拿到 Profile 对象本身
        main_workflow()

    print("\n  真实输出（sort=tottime）：")
    stats = pstats.Stats(pr, stream=sys.stdout)  # 把 Profile 原始数据转成可操作的统计对象，输出到 stdout
    stats.strip_dirs()              # 去掉文件路径前缀，只保留文件名
    stats.sort_stats("tottime")     # 按自身耗时排序（不含子函数）
    stats.print_stats(6)            # 只打印前 6 行；传字符串则按文件名/函数名过滤

    print("""
  字段说明（对照上方输出）：

  ncalls   调用次数
             200001  → 普通调用
             3/1     → 有递归：3 次总调用 / 1 次原始调用

  tottime  函数自身耗时，不含它调用的子函数     ← 找真正热点看这列
             slow_io tottime=0.032  说明拼接本身慢

  percall  tottime / ncalls（每次调用平均自身耗时）

  cumtime  含子函数的累计耗时                   ← 找慢调用链看这列
             main_workflow cumtime=0.090，但 tottime≈0
             说明它本身不慢，慢在它调用的子函数里

  percall  cumtime / ncalls

  filename:lineno(function)  精确定位到文件+行号+函数名

  sort_stats 排序参数：
    cumulative  累计时间，找慢调用链入口（先用这个）
    tottime     自身时间，确认真正的热点（再用这个）
    ncalls      调用次数，找高频调用
    filename    按文件名
""")


# ---------------------------------------------------------------------------
# ② 最简用法：cProfile.run
# ---------------------------------------------------------------------------

def demo02_run():
    """② cProfile.run：一行分析，输出到 stdout"""
    print("=" * 60)
    print("② cProfile.run（直接打印）")
    print("=" * 60)
    cProfile.run("main_workflow()", sort="cumulative")


# ---------------------------------------------------------------------------
# ③ Profile 对象 / context manager
# ---------------------------------------------------------------------------

def demo03_profile():
    """③ Profile 对象 + context manager：精确控制分析范围"""
    print("\n③ Profile 对象 + context manager")

    # 方式一：enable/disable 精确控制
    profiler = cProfile.Profile()
    profiler.enable()
    main_workflow()
    profiler.disable()

    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats("tottime")
    stats.print_stats(8)

    # 方式二：with 写法（更简洁，Python 3.8+）
    print("  -- with 写法 --")
    with cProfile.Profile() as pr:
        main_workflow()
    pstats.Stats(pr).strip_dirs().sort_stats("cumulative").print_stats(5)


# ---------------------------------------------------------------------------
# ④ pstats 过滤：只看特定文件 / 函数
# ---------------------------------------------------------------------------

def demo04_filter():
    """④ pstats 过滤：按文件名或函数名筛选行"""
    print("\n④ pstats 过滤")

    with cProfile.Profile() as pr:
        main_workflow()

    stats = pstats.Stats(pr)
    stats.strip_dirs()
    stats.sort_stats("tottime")

    print("  -- 只看本文件里的函数 --")
    stats.print_stats("01_cprofile")

    print("  -- 只看函数名含 io 的行 --")
    stats.print_stats("io")


# ---------------------------------------------------------------------------
# ⑤ pstats 调用关系：谁调用了谁
# ---------------------------------------------------------------------------

def demo05_callers_callees():
    """⑤ print_callers / print_callees：追调用链"""
    print("\n⑤ 调用关系")

    with cProfile.Profile() as pr:
        main_workflow()

    stats = pstats.Stats(pr)
    stats.strip_dirs()

    print("  -- slow_io 被谁调用 --")
    stats.print_callers("slow_io")

    print("  -- main_workflow 调用了谁 --")
    stats.print_callees("main_workflow")


# ---------------------------------------------------------------------------
# ⑥ 保存 .prof + 输出重定向 + 合并多次运行
# ---------------------------------------------------------------------------

def demo06_save_and_merge():
    """⑥ 保存 .prof、重定向输出、合并多次运行结果"""
    print("\n⑥ 保存 / 重定向 / 合并")
    prof1 = DATA_DIR / "run1.prof"
    prof2 = DATA_DIR / "run2.prof"

    with cProfile.Profile() as pr1:
        main_workflow()
    pr1.dump_stats(str(prof1))

    with cProfile.Profile() as pr2:
        slow_io(100_000)
    pr2.dump_stats(str(prof2))

    print(f"  已保存: {prof1.name}, {prof2.name}")
    print(f"  可视化: snakeviz {prof1}")

    # 输出重定向到字符串（日志 / 存文件用）
    buf = io.StringIO()
    pstats.Stats(str(prof1), stream=buf).strip_dirs().sort_stats("tottime").print_stats(3)
    report = buf.getvalue()
    print(f"  捕获报表 {len(report)} 字符，前两行:")
    for line in report.splitlines()[:2]:
        print(f"    {line}")

    # 合并两次运行：Stats 可接收多个文件，自动累加
    print("  -- 合并两次运行 --")
    merged = pstats.Stats(str(prof1), str(prof2))
    merged.strip_dirs().sort_stats("tottime").print_stats("slow_io")


# ---------------------------------------------------------------------------
# ⑦ 与 timeit 对比
# ---------------------------------------------------------------------------

def demo07_vs_timeit():
    """⑦ cProfile vs timeit：定位 vs 精确计时"""
    print("\n⑦ cProfile vs timeit")

    import timeit
    t = timeit.timeit("'-'.join(str(i) for i in range(1000))", number=1000)
    print(f"  timeit（1000次）: {t*1000:.2f} ms")

    print("""
  cProfile         → 整体分析，找慢在哪个函数    （全局视角）
  timeit           → 精确测量某个表达式           （局部精确）
  line_profiler    → 行级分析，cProfile 定位后再用（第三方）
""")


if __name__ == "__main__":
    demo01_explain()
    demo02_run()
    # demo03_profile()
    # demo04_filter()
    # demo05_callers_callees()
    # demo06_save_and_merge()
    # demo07_vs_timeit()
