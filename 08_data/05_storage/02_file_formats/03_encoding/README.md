# 编码修复

解决 CSV 文件在 Windows Excel 中打开乱码的问题。

| 文件 | 内容 |
|------|------|
| [01_fix_encoding.py](01_fix_encoding.py) | 批量修复工具：UTF-8 / GBK → utf-8-sig，支持自动检测编码 |

## 用法

```bash
python 01_fix_encoding.py data.csv                  # 原地修复
python 01_fix_encoding.py data.csv -o fixed.csv     # 写到新文件
python 01_fix_encoding.py *.csv                     # 批量修复
python 01_fix_encoding.py data.csv --from gbk       # GBK 源文件
python 01_fix_encoding.py data.csv --detect         # 自动检测编码（需 pip install chardet）
```

## 原理

Windows Excel 打开 CSV 默认用 GBK 编码，读到 UTF-8 文件就乱码。
给文件头加 BOM（`\xef\xbb\xbf`），Excel 识别到后自动切换为 UTF-8，乱码消失。

写出时直接避免：`df.to_csv("f.csv", encoding="utf-8-sig")`
