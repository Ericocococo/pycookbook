# Python Cookbook 常用命令入口
# 用法: make <目标>,例如 make install / make test / make lint

.PHONY: help install test lint format typecheck check clean

help:              ## 显示所有可用命令
	@echo "可用命令:"
	@echo "  make install    安装核心工具链 (pip install -e '.[dev]')"
	@echo "  make test       运行 pytest"
	@echo "  make lint       ruff 检查代码风格与常见错误"
	@echo "  make format     ruff 自动格式化"
	@echo "  make typecheck  mypy 类型检查"
	@echo "  make check      一次性跑 lint + typecheck + test"
	@echo "  make clean      清理缓存与构建产物"

install:           ## 安装核心开发工具链
	pip install -e ".[dev]"

test:              ## 运行测试
	pytest

lint:              ## 代码检查
	ruff check .

format:            ## 自动格式化
	ruff format .

typecheck:         ## 类型检查
	mypy .

check: lint typecheck test   ## 提交前一键全检

clean:             ## 清理缓存与产物
	rm -rf .pytest_cache .ruff_cache .mypy_cache .coverage htmlcov build dist
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
