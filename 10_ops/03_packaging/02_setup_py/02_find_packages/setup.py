from setuptools import setup, find_packages, find_namespace_packages

# ── 普通包（目录需有 __init__.py） ────────────────────────────────────────
setup(
    name="mypkg",
    version="0.1.0",
    python_requires=">=3.10",
    packages=find_packages(
        where="src",
        exclude=["tests*", "*._internal*"],
    ),
    package_dir={"": "src"},
)

# ── 命名空间包（目录无需 __init__.py，多个发行版共享同一顶级包名） ──────────
# setup(
#     packages=find_namespace_packages(where="src"),
#     package_dir={"": "src"},
# )
