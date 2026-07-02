"""numpy —— 随机数:重点 np.random.default_rng(新式 Generator API)

第三方库。Python 3.12 / numpy 2.x。运行: python 06_random.py

★ numpy 1.17+ 推荐用 np.random.default_rng() 创建独立的 Generator(生成器)对象,
  取代旧的全局 np.random.seed()/np.random.rand()。原因:
    1) 不污染全局状态,每个 rng 独立,多处代码互不干扰;
    2) 底层用更快更好的 PCG64 算法;
    3) 并行/可复现更可控(可 spawn 出独立子流)。
  旧 API(np.random.rand 等)仍能用,但新代码一律用 default_rng。
"""
import numpy as np


def demo01_create_rng():
    """① 创建生成器:传 seed(种子)即可复现

    rng.random(n) 生成 n 个服从 [0.0, 1.0) 连续均匀分布的浮点数
    (左闭右开,每个值等概率),等价于旧 API 的 np.random.rand(n)。
    """
    rng = np.random.default_rng(42)       # 固定种子 -> 每次运行结果相同
    print("① default_rng:")
    print("  type:", type(rng))
    print("  random(3) [0,1) 均匀:", rng.random(3))
    # 相同 seed 重建 -> 得到完全相同的序列
    rng2 = np.random.default_rng(42)
    print("  同种子复现:", rng2.random(3), "(与上面第一次一致)")


def demo02_distributions():
    """② 常见分布:均匀 / 正态 / 整数 / 泊松等

    各分布通俗解释:
      均匀分布 uniform    区间内每个值出现概率相等,如掷骰子、地图上随机撒点
                          ※ random(n) 固定生成 [0,1);uniform(low,high,n) 可指定
                             任意区间,即 random 是 uniform 在 [0,1) 上的特例
      正态分布 normal     钟形曲线,大量独立小因素叠加的自然结果(身高、测量误差);
                          由 均值 μ(曲线中心)与 标准差 σ(曲线胖瘦)两个参数决定
      标准正态 standard_normal
                          均值0、标准差1 的正态分布,相当于正态的"标准刻度尺"
      随机整数 integers   指定区间内等概率的随机整数(离散型均匀分布)
      泊松分布 poisson    单位时间/空间内"稀有独立事件发生次数"的分布,
                          如每分钟进店人数、每页错别字数;参数 λ(lam)= 平均发生率
    """
    rng = np.random.default_rng(0)
    print("② 各种分布:")
    print("  random((2,2)) 均匀[0,1):\n", rng.random((2, 2)))
    print("  uniform(-1,1,3):", rng.uniform(-1, 1, 3), "指定区间均匀")
    print("  normal(0,1,3) 正态:", rng.normal(0, 1, 3), "均值0 标准差1")
    print("  integers(0,10,5) 整数:", rng.integers(0, 10, 5), "[0,10) 整数")
    print("  poisson(3,5) 泊松:", rng.poisson(3, 5))
    print("  standard_normal((2,3)) 标准正态:\n", rng.standard_normal((2, 3)))


def demo03_choice_shuffle():
    """③ 抽样与打乱:choice / shuffle / permutation"""
    rng = np.random.default_rng(7)
    pool = np.arange(10)
    print("③ 抽样/打乱:")
    print("  choice 无放回抽 3:", rng.choice(pool, 3, replace=False))
    print("  choice 有放回抽 5:", rng.choice(pool, 5, replace=True))
    # 带权重抽样:p 指定每个元素被抽中的概率
    print("  choice 带权重:", rng.choice([0, 1], 8, p=[0.2, 0.8]), "(偏向 1)")
    print("  permutation 返回打乱的新数组:", rng.permutation(pool))
    a = np.arange(6)
    rng.shuffle(a)                        # 原地打乱(无返回值)
    print("  shuffle 原地打乱:", a)


def demo04_reproducible():
    """④ 可复现的正确姿势:把 rng 传进函数,而非依赖全局"""
    def sample_sum(rng, n):
        """接收 rng 参数 -> 调用方掌控随机性,便于测试复现"""
        return rng.normal(size=n).sum()

    print("④ 可复现模式:")
    r1 = np.random.default_rng(123)
    r2 = np.random.default_rng(123)
    print("  两个同种子 rng 结果相同:",
          np.isclose(sample_sum(r1, 100), sample_sum(r2, 100)))


def demo05_spawn_parallel():
    """⑤ 并行场景:从一个种子派生多个互不相关的子生成器"""
    parent = np.random.default_rng(2024)
    # spawn(n):派生 n 个独立子流,适合多进程/多线程各拿一个,保证互不重叠
    children = parent.spawn(3)
    print("⑤ spawn 派生独立子流(并行安全):")
    for i, child in enumerate(children):
        print(f"  子流 {i}:", child.integers(0, 100, 4))


def demo06_old_vs_new():
    """⑥ 新旧 API 对照(旧的仅作了解,新代码别用)"""
    print("⑥ 新旧对照:")
    print("  旧: np.random.seed(0); np.random.rand(3)  -> 改全局状态")
    print("  新: rng = np.random.default_rng(0); rng.random(3) -> 独立对象")
    # 旧 API 演示(仍可用)
    np.random.seed(0)
    print("  旧 API 结果:", np.random.rand(3))
    print("  新 API 结果:", np.random.default_rng(0).random(3))


if __name__ == "__main__":
    demo01_create_rng()
    print()
    demo02_distributions()
    print()
    demo03_choice_shuffle()
    print()
    demo04_reproducible()
    print()
    demo05_spawn_parallel()
    print()
    demo06_old_vs_new()
