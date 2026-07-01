#!/usr/bin/env sh
# flit 项目使用 flit 命令

flit install            # 开发模式（等价 pip install -e .）
flit build              # 生成 dist/
flit publish            # 发布到 PyPI
