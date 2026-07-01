"""
01_module_dunders —— 模块特殊属性（dunder 变量）

  module  = 模块（Python 源文件即一个模块）
  dunder  = double underscore，Python 约定的特殊名称前后各两个下划线

  01_overview.py  __file__ / __name__ / __doc__ / __package__ / __spec__ / __dict__ / __cached__ 全览

适用
  · 脚本判断"是否被直接运行"（__name__ == '__main__'）
  · 写库/包时声明版本、作者元数据（__version__ / __author__）
  · 控制 from pkg import * 的导出列表（__all__）
  · 调试模块加载位置（__file__ / __spec__）

不适用
  · 普通业务逻辑代码——不需要关注这些

核心速查
  __name__     # 直接运行时为 '__main__'，被导入时为模块全限定名
  __file__     # 当前文件绝对路径
  __doc__      # 模块 docstring
  __package__  # 所属包名；顶层脚本为 '' 或 None
  __all__      # 控制 from module import * 的导出列表
  __version__  # 约定俗成的版本号，需手动定义（非内置）
  __spec__     # 模块规范对象，含 name / origin
"""
