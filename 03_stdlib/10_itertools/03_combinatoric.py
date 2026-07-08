"""itertools 组合数学工具 —— product / permutations / combinations

Python 3.12。
运行: python 03_combinatoric.py

组合数学工具都是惰性生成器，按字典序输出，不产生中间 list。

演示：
  ① product：笛卡尔积（嵌套 for 循环的惰性等价）
  ② product(repeat=n)：自笛卡尔积
  ③ permutations：全排列（有序，无重复取）
  ④ combinations：组合（无序，无重复取）
  ⑤ combinations_with_replacement：允许重复取的组合
  ⑥ 实际场景：测试用例参数矩阵
  ⑦ 实际场景：密码暴力枚举（演示用，受限字符集）
"""

import itertools
import math


# ---------------------------------------------------------------------------
# ① product
# ---------------------------------------------------------------------------

def demo01_product():
    """① product(*iterables)：笛卡尔积，等价于嵌套 for"""
    print("① product 笛卡尔积")

    suits = ["♠", "♥", "♦", "♣"]
    ranks = ["A", "2", "3"]

    cards = list(itertools.product(ranks, suits))
    print(f"  ranks × suits ({len(cards)} 张):")
    for card in cards[:8]:
        print(f"    {card[0]}{card[1]}", end="  ")
    print("  ...")

    # 三维笛卡尔积
    coords = list(itertools.product([0, 1], [0, 1], [0, 1]))
    print(f"\n  3D 坐标 2×2×2 ({len(coords)} 个): {coords}")


# ---------------------------------------------------------------------------
# ② product repeat
# ---------------------------------------------------------------------------

def demo02_product_repeat():
    """② product(iterable, repeat=n)：自笛卡尔积 n 次"""
    print("\n② product repeat（自笛卡尔积）")

    # 等价于 product(it, it, it, ...) n 次
    bits = list(itertools.product([0, 1], repeat=3))
    print(f"  2位×3 = 所有3位二进制数 ({len(bits)} 个): {bits}")

    # DNA 序列（4碱基，长度2）
    dna2 = list(itertools.product("ACGT", repeat=2))
    print(f"  DNA 2聚体 ({len(dna2)} 种): {[''.join(p) for p in dna2]}")

    # 总数 = len(iterable) ** repeat
    print(f"  len('ACGT')**3 = {len('ACGT')**3} 种 3聚体")


# ---------------------------------------------------------------------------
# ③ permutations
# ---------------------------------------------------------------------------

def demo03_permutations():
    """③ permutations(iterable, r=None)：全排列，r 省略则取全部"""
    print("\n③ permutations 全排列")

    items = ["A", "B", "C"]

    # r=None：取所有元素的全排列（n! 种）
    all_perms = list(itertools.permutations(items))
    print(f"  permutations(['A','B','C'])  {len(all_perms)}种 ({math.factorial(3)}!): {all_perms}")

    # r=2：取 2 个的有序排列（A_n^r = n!/(n-r)!）
    perms2 = list(itertools.permutations(items, 2))
    print(f"  permutations(['A','B','C'],2) {len(perms2)}种: {perms2}")

    # 注意：(A, B) 和 (B, A) 是不同的排列
    print(f"  ('A','B') 和 ('B','A') 都在里面: {('A','B') in perms2 and ('B','A') in perms2}")


# ---------------------------------------------------------------------------
# ④ combinations
# ---------------------------------------------------------------------------

def demo04_combinations():
    """④ combinations(iterable, r)：组合，无序无重复"""
    print("\n④ combinations 组合")

    items = ["A", "B", "C", "D"]

    # C(4, 2) = 6 种
    combs2 = list(itertools.combinations(items, 2))
    print(f"  combinations(4取2) {len(combs2)}种: {combs2}")

    # C(4, 3) = 4 种
    combs3 = list(itertools.combinations(items, 3))
    print(f"  combinations(4取3) {len(combs3)}种: {combs3}")

    # 与 permutations 的区别：(A,B) 和 (B,A) 视为同一组合
    all_combs = list(itertools.combinations("ABCD", 2))
    print(f"  ('A','B') in combs: {('A','B') in all_combs}")
    print(f"  ('B','A') in combs: {('B','A') in all_combs}")

    # 实际场景：所有可能的配对（社交/比赛）
    players = ["Alice", "Bob", "Carol", "Dave"]
    matches = list(itertools.combinations(players, 2))
    print(f"\n  循环赛对阵 ({len(matches)} 场):")
    for m in matches:
        print(f"    {m[0]} vs {m[1]}")


# ---------------------------------------------------------------------------
# ⑤ combinations_with_replacement
# ---------------------------------------------------------------------------

def demo05_cwr():
    """⑤ combinations_with_replacement：允许同一元素重复取"""
    print("\n⑤ combinations_with_replacement")

    items = ["A", "B", "C"]

    # 允许重复：(A, A) (A, B) (A, C) (B, B) (B, C) (C, C)
    cwr = list(itertools.combinations_with_replacement(items, 2))
    print(f"  CWR(3取2) {len(cwr)}种: {cwr}")

    # 与 combinations 对比
    combs = list(itertools.combinations(items, 2))
    print(f"  C(3取2)   {len(combs)}种: {combs}")

    # 实际场景：零钱组合（面值 1, 2, 5，取 3 枚，面值可重复）
    coins = [1, 2, 5]
    combos = [(c, sum(c)) for c in itertools.combinations_with_replacement(coins, 3)]
    print(f"\n  3枚硬币组合（面值可重复）:")
    for combo, total in combos:
        print(f"    {combo} → 合计 {total}")


# ---------------------------------------------------------------------------
# ⑥ 实际场景：测试参数矩阵
# ---------------------------------------------------------------------------

def demo06_test_matrix():
    """⑥ 实际场景：生成测试参数矩阵（参数化测试）"""
    print("\n⑥ 测试参数矩阵")

    # 所有参数组合
    protocols = ["http", "https"]
    hosts = ["localhost", "example.com"]
    ports = [80, 443, 8080]
    timeouts = [5, 30]

    cases = list(itertools.product(protocols, hosts, ports, timeouts))
    print(f"  参数组合数: {len(cases)}")
    print(f"  前 5 个测试用例:")
    for proto, host, port, timeout in cases[:5]:
        print(f"    {proto}://{host}:{port}  timeout={timeout}s")

    # 用 combinations 生成两两功能交叉测试
    features = ["缓存", "压缩", "加密", "日志"]
    pairs = list(itertools.combinations(features, 2))
    print(f"\n  功能两两交叉测试 ({len(pairs)} 对):")
    for a, b in pairs:
        print(f"    {a} + {b}")


# ---------------------------------------------------------------------------
# ⑦ 实际场景：密码枚举（演示受限字符集）
# ---------------------------------------------------------------------------

def demo07_brute_force():
    """⑦ 枚举所有 2 位小写字母组合（演示用，不含大规模攻击）"""
    print("\n⑦ 2位字母枚举（演示）")

    charset = "abc"
    length = 2

    all_passwords = ["".join(p) for p in itertools.product(charset, repeat=length)]
    print(f"  字符集 {charset!r}，长度 {length}，共 {len(all_passwords)} 种:")
    print(f"  {all_passwords}")

    # 实际评估：26字母 × 长度8 = 26^8 ≈ 2000亿种
    # 26字母+数字+特殊字符(62) × 长度12 = 62^12 ≈ 3×10^21 种
    print(f"\n  纯小写字母长度8: {26**8:,} 种")
    print(f"  62字符长度12:    {62**12:,} 种")


if __name__ == "__main__":
    demo01_product()
    demo02_product_repeat()
    demo03_permutations()
    demo04_combinations()
    demo05_cwr()
    demo06_test_matrix()
    demo07_brute_force()
