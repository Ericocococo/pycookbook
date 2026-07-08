# itertools — 迭代器工具箱

`itertools` 提供高效的迭代器构建块，全部返回迭代器（惰性），不产生中间列表。
组合使用可以写出简洁、高性能的数据流处理管道。

| 文件 | 内容 |
|------|------|
| [01_infinite.py](01_infinite.py) | `count`/`cycle`/`repeat`：无穷迭代器，配合 `islice` 截断 |
| [02_finite.py](02_finite.py) | `chain`/`islice`/`takewhile`/`dropwhile`/`zip_longest`/`accumulate` 等 |
| [03_combinatoric.py](03_combinatoric.py) | `product`/`permutations`/`combinations`/`combinations_with_replacement` |

## 核心概念

| 函数 | 一句话 |
|------|--------|
| `count(n, step)` | 从 n 开始以 step 为步长无穷递增 |
| `cycle(it)` | 无限循环一个序列 |
| `repeat(x, n)` | 重复 x，n 次（省略 n 则无限） |
| `chain(*its)` | 依次串联多个迭代器 |
| `islice(it, stop)` | 切片（不支持负索引） |
| `takewhile(pred, it)` | 取满足条件的前缀，首次失败就停 |
| `dropwhile(pred, it)` | 跳过满足条件的前缀，首次失败后全取 |
| `zip_longest(*its, fillvalue)` | 以最长者为准，短的补 fillvalue |
| `accumulate(it, func)` | 累积中间值序列（默认加法） |
| `product(*its, repeat)` | 笛卡尔积 |
| `permutations(it, r)` | 全排列 |
| `combinations(it, r)` | 组合（无重复，有序） |

## 核心速查

```python
import itertools as it

# 无穷 → 用 islice 截断
list(it.islice(it.count(10, 2), 5))   # [10, 12, 14, 16, 18]
list(it.islice(it.cycle("AB"), 5))    # ['A', 'B', 'A', 'B', 'A']

# 串联 + 切片
list(it.chain([1, 2], [3, 4], [5]))   # [1, 2, 3, 4, 5]

# 累积
list(it.accumulate([1, 2, 3, 4]))     # [1, 3, 6, 10]

# 组合数学
list(it.product("AB", repeat=2))      # [('A','A'),('A','B'),('B','A'),('B','B')]
list(it.combinations("ABC", 2))       # [('A','B'),('A','C'),('B','C')]
```
