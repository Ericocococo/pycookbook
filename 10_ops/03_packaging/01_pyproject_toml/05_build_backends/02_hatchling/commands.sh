#!/usr/bin/env sh
# hatchling 项目使用 hatch 命令，不需要 Makefile

hatch env create        # 创建虚拟环境
hatch run test          # 跑测试（对应 pyproject.toml [tool.hatch.envs.default.scripts]）
hatch run lint          # 跑 ruff
hatch build             # 生成 dist/
hatch publish           # 发布到 PyPI
