# pyproject.toml —— 现代 Python 包配置标准（PEP 517/518/621）

| 文件 | 内容 |
|------|------|
| `01_minimal/` | 最小结构：name / version / requires-python |
| `02_dependencies/` | dependencies / optional-dependencies / extras |
| `03_entry_points/` | console_scripts 命令行入口，含 src/mypkg/cli.py |
| `04_tool_config/` | 合并工具配置：ruff / pytest / mypy / coverage |
| `05_build_backends/` |  |
| `01_setuptools/` | 最通用，支持 C 扩展，src-layout，动态版本 |
| `02_hatchling/` | 配置简洁，版本自动读文件，hatch 工作流 |
| `03_flit/` | 极简小库，约定大于配置 |


## 适用

- Python 3.10+ 新项目的首选配置方式（单文件统一所有工具配置）
- 需要 pip install -e . / python -m build 打包发布

## 不适用

- 需要动态构建逻辑（C 扩展复杂 Makefile）→ 保留 setup.py 或用 meson-python
- 维护已有 setup.py 的老项目且无迁移计划   → 不强制迁移

## 核心速查

```toml
[build-system]
requires      = ["setuptools>=68"]
build-backend = "setuptools.backends.legacy:build"

[project]
name            = "mypkg"
version         = "0.1.0"
requires-python = ">=3.10"
dependencies    = ["requests>=2.28", "pandas"]

[project.optional-dependencies]
dev = ["pytest", "ruff"]

[project.scripts]
mypkg = "mypkg.cli:main"

```

## 常用命令

```bash
pip install -e ".[dev]"   # 开发模式安装
python -m build           # 生成 dist/
twine upload dist/*       # 发布到 PyPI
```
