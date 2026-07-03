"""importlib.metadata —— 读取已安装包的元数据

标准库。Python 3.12。
运行: python 03_metadata.py

importlib.metadata 让你查询 pip 安装的任何包的信息：
版本号、依赖、作者、入口点（CLI 命令注册）等。
数据来源是包安装时写入的 METADATA / PKG-INFO 文件，不需要导入包本身。

演示：
  ① version()：获取包版本号
  ② metadata()：读取完整包元数据（作者、主页等）
  ③ requires()：读取依赖列表
  ④ packages_distributions()：模块名 → 包名的反查
  ⑤ entry_points()：读取命令行入口点（CLI 注册信息）
  ⑥ packages()：列出所有已安装包
"""
import importlib.metadata as meta


def demo01_version():
    """① version()：最常用的操作

    直接返回版本字符串，包名大小写不敏感。
    包不存在时抛 PackageNotFoundError。
    """
    print("① 包版本")

    # 查询标准库附带/几乎肯定安装的包
    for pkg in ["pip", "setuptools"]:
        try:
            v = meta.version(pkg)
            print(f"  {pkg}: {v}")
        except meta.PackageNotFoundError:
            print(f"  {pkg}: 未安装")

    # 在代码里做版本兼容判断
    try:
        pip_ver = meta.version("pip")
        major = int(pip_ver.split(".")[0])
        print(f"  pip 主版本号: {major}")
        if major >= 21:
            print("  pip >= 21，支持 --dry-run 标志")
    except meta.PackageNotFoundError:
        pass


def demo02_metadata():
    """② metadata()：读取完整包信息

    返回类字典对象（email.message.Message），
    字段名对应 PEP 566 / PEP 643 的 METADATA 字段。

    常用字段：
      Name, Version, Summary, Home-page, Author, License, Requires-Python
    """
    print("\n② 完整元数据")

    try:
        m = meta.metadata("pip")
        fields = ["Name", "Version", "Summary", "Author-email", "Requires-Python"]
        for field in fields:
            val = m[field]
            if val:
                print(f"  {field}: {val}")
    except meta.PackageNotFoundError:
        print("  pip 未安装，跳过")


def demo03_requires():
    """③ requires()：依赖列表

    返回 PEP 508 格式的依赖字符串列表，每条形如：
      "requests>=2.28"
      "urllib3 ; extra == 'security'"
      "pytest ; extra == 'dev'"

    术语：
      extra       可选依赖分组，pip install pkg[dev] 时才安装带 extra 标记的依赖
      marker      环境标记，如 "python_version < '3.8'"，描述依赖生效的条件
    """
    print("\n③ 依赖列表")

    for pkg in ["pip", "setuptools"]:
        try:
            deps = meta.requires(pkg)
            if deps:
                print(f"  {pkg} 的依赖（前 5 条）:")
                for dep in deps[:5]:
                    print(f"    {dep}")
                if len(deps) > 5:
                    print(f"    ...共 {len(deps)} 条")
            else:
                print(f"  {pkg}: 无依赖")
        except meta.PackageNotFoundError:
            print(f"  {pkg}: 未安装")


def demo04_packages_distributions():
    """④ packages_distributions()：模块名 → 包名反查

    解决"我 import 的是 'PIL'，但 pip 里叫什么名字？"的问题。

    返回 dict，键是模块顶层名，值是包名列表（可能一对多）。
    """
    print("\n④ 模块名 → 包名反查")

    mapping = meta.packages_distributions()

    # 查几个常见的"模块名 ≠ 包名"例子
    interesting = ["PIL", "cv2", "sklearn", "bs4", "yaml", "dotenv"]
    for mod_name in interesting:
        pkg_names = mapping.get(mod_name, [])
        if pkg_names:
            print(f"  import {mod_name!r} → pip 包: {pkg_names}")
        else:
            print(f"  import {mod_name!r} → 未发现（可能未安装）")

    # 展示几个已安装的映射
    print("  已安装映射示例（前 8 条）:")
    shown = 0
    for mod, pkgs in sorted(mapping.items()):
        if mod != pkgs[0]:   # 只展示模块名 ≠ 包名的情况，更有意思
            print(f"    {mod!r:20s} → {pkgs}")
            shown += 1
            if shown >= 8:
                break


def demo05_entry_points():
    """⑤ entry_points()：CLI 入口点

    包安装时可以在 pyproject.toml / setup.cfg 里注册入口点：
      [project.scripts]
      my-tool = "mypackage.cli:main"

    安装后 pip 生成 my-tool 可执行文件，调用 mypackage.cli.main()。
    entry_points() 让你程序化地发现这些注册信息。

    术语：
      group       入口点分组，"console_scripts" 是 CLI 命令，
                  其他组用于插件系统（如 pytest 的 pytest11）
      value       "module:attr" 格式的引用字符串
    """
    print("\n⑤ entry_points 入口点")

    # 查看 console_scripts 分组（所有 CLI 命令）
    scripts = meta.entry_points(group="console_scripts")
    print(f"  已安装的 CLI 命令（共 {len(scripts)} 个，展示前 8 个）:")
    for ep in list(scripts)[:8]:
        print(f"    {ep.name:20s} → {ep.value}")

    # 加载入口点指向的函数（不用手动 import）
    # ep.load() 等价于 from module import attr
    if scripts:
        ep = list(scripts)[0]
        try:
            func = ep.load()
            print(f"  ep.load() 加载 '{ep.name}': {func}")
        except Exception as e:
            print(f"  ep.load() 示意（实际加载可能需要完整环境）: {e}")


def demo06_list_all_packages():
    """⑥ packages()：列出所有已安装包

    meta.packages_distributions() 包含了所有已安装包的模块映射。
    要获取所有包名+版本，用 meta.distributions()。
    """
    print("\n⑥ 所有已安装包")

    dists = list(meta.distributions())
    print(f"  已安装包总数: {len(dists)}")

    # 按名称排序，展示前 10 个
    sorted_dists = sorted(dists, key=lambda d: d.metadata["Name"].lower())
    print("  前 10 个包:")
    for d in sorted_dists[:10]:
        name = d.metadata["Name"]
        version = d.metadata["Version"]
        print(f"    {name:30s} {version}")


if __name__ == "__main__":
    demo01_version()
    demo02_metadata()
    demo03_requires()
    demo04_packages_distributions()
    demo05_entry_points()
    demo06_list_all_packages()
