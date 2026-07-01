from setuptools import setup, find_packages

setup(
    name="mypkg",
    version="0.1.0",
    description="一句话描述",
    author="Alice",
    author_email="alice@example.com",
    python_requires=">=3.10",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.28",
    ],
    extras_require={
        "dev": ["pytest", "ruff"],
    },
)
