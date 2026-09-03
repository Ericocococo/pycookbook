# 格式转换 —— 文件格式之间互转

不同格式的文件互相转换：xlsx → csv、json → csv、parquet → csv 等。
与 [01_formats/](../01_formats/) 的区别：那边学单个格式的读写，这边做格式间的实际转换。

| 文件 | 内容 |
|------|------|
| [01_xlsx_to_csv.py](01_xlsx_to_csv.py) | Excel → CSV：单表 / 多 Sheet / 批量 / 命令行工具 |

## 核心速查

```python
import pandas as pd

# 最简单的 xlsx → csv（两行搞定）
pd.read_excel("input.xlsx").to_csv("output.csv", index=False, encoding="utf-8-sig")

# 多 Sheet → 每个 Sheet 各一个 csv
sheets = pd.read_excel("input.xlsx", sheet_name=None)
for name, df in sheets.items():
    df.to_csv(f"output_{name}.csv", index=False, encoding="utf-8-sig")
```
