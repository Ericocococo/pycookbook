from setuptools import setup, find_packages

# 旧写法——等价配置见同目录 pyproject.toml
setup(
    name="mypkg",
    version="0.1.0",
    description="一句话描述",
    python_requires=">=3.10",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["requests>=2.28", "pandas>=2.0"],
    extras_require={"dev": ["pytest", "ruff"]},
    entry_points={"console_scripts": ["mypkg=mypkg.cli:main"]},
)
