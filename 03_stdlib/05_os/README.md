# os —— 操作系统接口(路径 / 目录 / 文件 / 环境变量 / 进程)

| 文件 | 内容 |
|------|------|
| `01_path.py` | os.path 字符串路径函数:join / split / abspath / exists / getsize / commonpath 等 |
| `02_dir_ops.py` | 目录操作:getcwd / listdir / scandir(DirEntry) / makedirs / walk(含剪枝) |
| `03_file_ops.py` | 文件操作:remove / rename / replace / stat / access / chmod / link / symlink |
| `04_env.py` | 环境变量:os.environ 读写 / expandvars / 常用变量 / 子进程继承 |
| `05_process.py` | 进程与系统常量:name/sep/pathsep / pid / cpu_count / urandom / os.times |


## 适用

- 低级文件系统操作(stat / chmod / link)，不需要面向对象封装时
- 读写、传递环境变量（subprocess 继承）
- 获取进程信息（pid / ppid / cpu_count）和密码学随机数（urandom）
- 维护旧代码或需要纯字符串路径函数（os.path）

## 不适用

- 拼路径、创建目录树、递归遍历 → `pathlib`（面向对象，更现代，见 02_pathlib）
- 整目录复制 / 移动 / 归档 → `shutil`（见 03_shutil）
- 深度进程控制（管道 / 超时 / 返回码 / 并发）→ `subprocess`

## 核心速查

```python
import os, os.path

# 路径字符串（os.path）
os.path.join('a', 'b', 'c.txt')      # 'a\\b\\c.txt'（Windows）/ 'a/b/c.txt'（Unix）
os.path.abspath('rel')               # 当前目录 + 相对路径 → 绝对路径
os.path.dirname('/a/b.txt')          # '/a'
os.path.basename('/a/b.txt')         # 'b.txt'
os.path.splitext('b.txt')            # ('b', '.txt')
os.path.exists('/a/b.txt')           # True / False
os.path.getsize('/a/b.txt')          # 文件字节数

# 目录
os.getcwd()                          # 当前工作目录（绝对路径字符串）
os.makedirs('a/b/c', exist_ok=True)  # 递归建目录，exist_ok 防报错
list(os.scandir('.'))                # DirEntry 列表（比 listdir 快，有属性缓存）
for root, dirs, files in os.walk('.'): ...  # 递归遍历，dirs[:] 修改可剪枝

# 文件
os.remove('f.txt')                   # 删文件（不存在则 FileNotFoundError）
os.rename('old', 'new')              # 重命名 / 移动
os.replace('src', 'dst')             # 原子覆盖替换（3.3+）
os.stat('f.txt').st_size             # 文件大小（字节）
os.access('f.txt', os.W_OK)         # 检查读写执行权限

# 环境变量
os.environ.get('HOME', '')           # 读（不存在返回默认值）
os.environ['MY_VAR'] = 'val'        # 写（对子进程立即可见）
os.path.expandvars('%PATH%')         # Windows：展开 %VAR%；Unix：展开 $VAR

# 进程
os.getpid()                          # 当前进程 PID
os.cpu_count()                       # 逻辑 CPU 核心数
os.urandom(16)                       # 16 字节密码学安全随机数
```
