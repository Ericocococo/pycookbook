.PHONY: install build ext clean

install:
	pip install -e .

ext:
	python setup.py build_ext --inplace   # 原地编译，.so 放在源码旁

build:
	python -m build

clean:
	rm -rf dist/ build/ *.egg-info
	find . -name "*.so" -delete
	find . -name "*.pyd" -delete
