"""
05_build_backends —— Python 包构建后端对比

  01_setuptools/ 最通用，支持 C 扩展，src-layout，老项目迁移首选
  02_hatchling/  配置简洁，版本自动读文件，hatch 工作流
  03_flit/       极简小库，约定大于配置，零额外配置

适用
  · 选择/切换构建后端时参考

不适用
  · 含 C++/CUDA 的大型项目 → scikit-build-core / meson-python

核心速查（三选一写入 [build-system]）
  requires = ["setuptools>=68", "wheel"]
  build-backend = "setuptools.backends.legacy:build"

  requires = ["hatchling"]
  build-backend = "hatchling.build"

  requires = ["flit_core>=3.9"]
  build-backend = "flit_core.buildapi"
"""
