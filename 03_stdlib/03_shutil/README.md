# shutil —— 高层文件与目录操作(shell utilities)

| 文件 | 内容 |
|------|------|
| `01_copy.py` | 复制:copyfile / copy / copy2 / copytree(含 ignore、dirs_exist_ok) |
| `02_move_remove.py` | 移动与删除:move / rmtree(含 onexc 错误回调) |
| `03_archive.py` | 归档压缩:make_archive / unpack_archive(zip / tar / gztar 等) |
| `04_disk_which.py` | 工具:disk_usage 磁盘用量 / which 查可执行文件 / 终端尺寸 |


## 适用

- 整个文件/目录树的复制、移动、递归删除(比自己 os.walk 省事)
- 一行打包/解包 zip、tar.gz 归档
- 查磁盘剩余空间、定位可执行程序路径

## 不适用

- 只拼路径、查属性、遍历 → pathlib(见 02_pathlib)
- 单文件精细读写、字节流 → open / pathlib.read_bytes
- 跨机器传输 → paramiko(sftp) / rsync

## 核心速查

```python
import shutil

shutil.copy2('a.txt', 'b.txt')            # 复制文件(含元数据:时间戳等)
shutil.copytree('src', 'dst', dirs_exist_ok=True)  # 递归复制目录
shutil.move('a.txt', 'sub/')              # 移动(跨盘会退化为复制+删除)
shutil.rmtree('sub')                      # 递归删除整个目录树(危险,不可逆!)
shutil.make_archive('bak', 'zip', 'src')  # 打包成 bak.zip
shutil.unpack_archive('bak.zip', 'out')   # 解包
shutil.disk_usage('.')                    # (total, used, free) 字节
shutil.which('python')                    # 可执行文件绝对路径,找不到返 None
```
