.PHONY: install ext build clean

install:
	pip install cython numpy
	pip install -e .

ext:
	python setup.py build_ext --inplace   # 编译 .pyx → .so

annotate:
	cython --annotate src/mypkg/*.pyx     # 生成 .html 性能标注文件

build:
	python -m build

clean:
	rm -rf dist/ build/ *.egg-info
	find . -name "*.so" -o -name "*.pyd" -o -name "*.c" -o -name "*.html" | xargs rm -f
