"""CSV 编码修复工具：解决 Windows Excel 打开乱码问题

依赖: pip install chardet   （自动检测编码时需要）
Python 3.12。

用法:
    python fix_csv_encoding.py a.csv                  # 原地转换（UTF-8 → utf-8-sig）
    python fix_csv_encoding.py a.csv -o b.csv         # 写到新文件
    python fix_csv_encoding.py *.csv                  # 批量原地转换
    python fix_csv_encoding.py a.csv --from gbk       # 源文件是 GBK
    python fix_csv_encoding.py a.csv --detect         # 自动检测源编码

原理：Windows Excel 打开 CSV 默认用系统编码（GBK），读到 UTF-8 文件就乱码。
     给文件头加 BOM（\xef\xbb\xbf），Excel 识别到 BOM 就会以 UTF-8 打开，乱码消失。
"""
import argparse
import pathlib
import sys


def detect_encoding(path: pathlib.Path, sample_bytes: int = 10_000) -> str:
    """用 chardet 自动检测文件编码"""
    try:
        import chardet
    except ImportError:
        print("自动检测需要安装: pip install chardet", file=sys.stderr)
        sys.exit(1)

    raw = path.read_bytes()[:sample_bytes]
    result = chardet.detect(raw)
    enc = result.get("encoding") or "utf-8"
    confidence = result.get("confidence", 0)
    print(f"  检测到编码: {enc}（置信度 {confidence:.0%}）")
    return enc


def fix_encoding(src: pathlib.Path, dst: pathlib.Path, from_enc: str = "utf-8"):
    """把 CSV 转为 utf-8-sig（带 BOM），Windows Excel 可正常打开。

    src: 源文件路径
    dst: 目标文件路径（可与 src 相同，即原地覆盖）
    from_enc: 源文件编码
    """
    raw = src.read_bytes()

    # 已有 BOM → 去掉，避免写入双重 BOM
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]

    text = raw.decode(from_enc)
    dst.write_bytes(b"\xef\xbb\xbf" + text.encode("utf-8"))


def main():
    ap = argparse.ArgumentParser(
        description="CSV 编码修复：UTF-8/GBK → utf-8-sig，解决 Excel 乱码",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python fix_csv_encoding.py data.csv                 # 原地修复
  python fix_csv_encoding.py data.csv -o fixed.csv    # 写到新文件
  python fix_csv_encoding.py *.csv                    # 批量修复
  python fix_csv_encoding.py data.csv --from gbk      # GBK 源文件
  python fix_csv_encoding.py data.csv --detect        # 自动检测编码
        """,
    )
    ap.add_argument("files", nargs="+", help="CSV 文件路径（支持多个）")
    ap.add_argument("-o", "--output", help="输出路径（仅单文件时有效，默认原地覆盖）")
    ap.add_argument("--from", dest="from_enc", default="utf-8",
                    help="源文件编码，默认 utf-8；GBK 文件传 gbk")
    ap.add_argument("--detect", action="store_true",
                    help="用 chardet 自动检测源编码（覆盖 --from）")
    args = ap.parse_args()

    paths = [pathlib.Path(f) for f in args.files]

    # 检查文件是否存在
    missing = [p for p in paths if not p.exists()]
    if missing:
        for p in missing:
            print(f"  文件不存在: {p}", file=sys.stderr)
        sys.exit(1)

    # 单文件 + 指定输出路径
    if args.output and len(paths) == 1:
        src = paths[0]
        dst = pathlib.Path(args.output)
        enc = detect_encoding(src) if args.detect else args.from_enc
        fix_encoding(src, dst, enc)
        print(f"  {src} → {dst}")
        return

    # 批量原地转换
    for src in paths:
        enc = detect_encoding(src) if args.detect else args.from_enc
        fix_encoding(src, src, enc)
        print(f"  {src}（已修复）")


if __name__ == "__main__":
    main()
