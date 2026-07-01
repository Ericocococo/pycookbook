"""
pathlib —— 面向对象的路径操作

  01_basic.py       Path 对象创建、各部分属性（name / stem / suffix / parts / anchor）、PurePath
  02_navigate.py    / 运算符拼接、with_name / stem / suffix 修改、resolve / relative_to / parents
  03_query.py       exists / is_file / is_dir / stat 查询，glob / rglob / iterdir 遍历
  04_read_write.py  read_text / write_text / read_bytes / write_bytes / open 读写
  05_operations.py  mkdir / touch / rename / unlink / rmdir 文件系统操作

适用
  · Python 3.4+ 任何路径操作，跨平台首选
  · 替代 os.path 的现代写法，/ 运算符拼接更直观

不适用
  · 需要低级 fd / syscall    → os 模块
  · 只做简单字符串拼接且已有 os.path 代码 → 维持原样即可

核心速查
  from pathlib import Path
  p = Path('data/input.csv')
  p.parent / 'output' / p.name   # 路径拼接
  p.stem, p.suffix, p.name       # 'input', '.csv', 'input.csv'
  p.exists(), p.is_file()        # 查询
  p.read_text(encoding='utf-8')  # 读取
  p.write_text('...', encoding='utf-8')    # 写入
  list(Path('.').glob('**/*.py'))          # 遍历
  p.mkdir(parents=True, exist_ok=True)    # 创建目录
"""
