"""Excel → CSV 格式转换

依赖: pip install pandas openpyxl
Python 3.12。运行: python 01_xlsx_to_csv.py

演示：
  ① 单表转换：一个 xlsx 文件 → 一个 csv 文件
  ② 多 Sheet 转换：每个 Sheet 各生成一个 csv
  ③ 批量转换：目录下所有 .xlsx 一次性转完

xlsx_to_csv() 是核心转换函数，通过 sheet 参数控制三种模式：
  - sheet=0（默认）：转第一个 Sheet
  - sheet="AAPL"：转指定 Sheet
  - sheet="all"：每个 Sheet 各生成一个 csv
"""
import pathlib

import numpy as np
import pandas as pd

DATA_DIR = pathlib.Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# 核心转换函数
# ---------------------------------------------------------------------------

def xlsx_to_csv(xlsx_path: pathlib.Path, output: pathlib.Path = None,
                sheet=0, encoding: str = "utf-8-sig"):
    """xlsx → csv 转换

    Args:
        xlsx_path: 输入的 xlsx 文件路径
        output: 输出路径（默认同目录同名 .csv；sheet="all" 时为输出目录）
        sheet: Sheet 选择
            - 0（默认）→ 第一个 Sheet
            - 具体 Sheet 名（如 "AAPL"）→ 指定 Sheet
            - "all" → 每个 Sheet 各一个 csv
        encoding: csv 编码（默认 utf-8-sig，兼容 Windows Excel）
    """
    if sheet == "all":
        # 所有 Sheet 各一个 csv
        out_dir = output or xlsx_path.parent
        sheets = pd.read_excel(xlsx_path, sheet_name=None, engine="openpyxl")
        stem = xlsx_path.stem  # 文件名不含后缀，如 "multi_sheet"
        for name, sheet_df in sheets.items():
            # 输出文件名格式: multi_sheet_AAPL.csv
            csv_path = out_dir / f"{stem}_{name}.csv"
            sheet_df.to_csv(csv_path, index=False, encoding=encoding)
            print(f"  Sheet [{name}] → {csv_path.name}  ({len(sheet_df)} 行)")
    else:
        # 单个 Sheet
        csv_path = output or xlsx_path.with_suffix(".csv")
        data = pd.read_excel(xlsx_path, sheet_name=sheet, engine="openpyxl")
        # encoding="utf-8-sig" 让 Windows Excel 打开不乱码
        data.to_csv(csv_path, index=False, encoding=encoding)
        print(f"  {xlsx_path.name} → {csv_path.name}  ({len(data)} 行)")


def make_test_xlsx():
    """生成演示用的单表和多 Sheet xlsx 文件"""
    rng = np.random.default_rng(42)
    N = 50
    _df = pd.DataFrame({
        "date":   pd.date_range("2026-01-01", periods=N, freq="D"),
        "symbol": rng.choice(["AAPL", "MSFT", "GOOG"], N),
        "close":  rng.uniform(100, 500, N).round(2),
        "volume": rng.integers(100_000, 5_000_000, N),
    })

    # 单表 xlsx
    single = DATA_DIR / "single.xlsx"
    _df.to_excel(single, index=False, engine="openpyxl")

    # 多 Sheet xlsx
    multi = DATA_DIR / "multi_sheet.xlsx"
    with pd.ExcelWriter(multi, engine="openpyxl") as w:
        _df[_df["symbol"] == "AAPL"].to_excel(w, sheet_name="AAPL", index=False)
        _df[_df["symbol"] == "MSFT"].to_excel(w, sheet_name="MSFT", index=False)
        _df[_df["symbol"] == "GOOG"].to_excel(w, sheet_name="GOOG", index=False)

    return single, multi


if __name__ == "__main__":
    _single, _multi = make_test_xlsx()
    print(_single)
    print(_multi)

    _single = DATA_DIR / "利润表_688836.xlsx"


    print("① 单表转换")
    xlsx_to_csv(_single)

    # print("\n② 多 Sheet 转换")
    # xlsx_to_csv(_multi, sheet="all")
    #
    # print("\n③ 批量转换（目录下所有 xlsx）")
    # for _f in sorted(DATA_DIR.glob("*.xlsx")):
    #     xlsx_to_csv(_f)
