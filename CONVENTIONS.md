# 习惯约定

> 本仓库在协作/填充配方过程中形成的习惯,和 [目录设计文档](STRUCTURE.md) 里的
> "贯穿全库的约定"互补——那边讲**结构规则**,这边讲**动手时的习惯**。

---

## 目录与结构

1. **用到再建,不建空壳** —— 目录做到哪块才建哪块,不预先铺一堆空目录占位
   (空目录 git 本来也不跟踪)。设计文档里列出的是"规划",不代表磁盘上都得先建出来。
2. **所有层级目录带两位序号前缀**(`01_ 02_ ...`),阅读顺序即学习/工程顺序;
   工程约定目录(`tests/`、`.github/`)按惯例不加号。
3. **一个库/主题一个子目录,内部按功能拆成多个带序号 `.py`** ——
   以 [`03_stdlib/01_argparse/`](03_stdlib/01_argparse/) 为范式(basic/types/actions/...),
   **不平铺成单个大文件**。
   - **子目录名** 要说明内容，缩写和专业名词在 `00_description.py` 的 docstring 里解释，
     如 `01_module_dunders`（module dunder = 模块双下划线特殊属性）。
4. **每个主题都放在自己的子目录里**，不直接把 `.py` 散放在上级目录 ——
   以 `03_stdlib/01_argparse/`、`01_language/02_advanced/01_module_dunders/` 为范式。
5. **只有叶子目录（直接含 `.py` 配方的目录）才建 `00_description.py`**，中间层目录不加 ——
   `print` 出该目录所有文件及一行内容摘要，`python 00_description.py` 即可查看导航；序号 `00` 确保排在最前。
6. **英文术语、缩写、专业名词必须解释** —— 包括英文缩写（`argv`/`nargs`/`dunder`）、
   中文缩写、框架专有名词（`schema`/`predicate pushdown`）等，让读者不查文档也能读懂。
   解释位置：短的一句话能说清的放行内注释；较长或多行解释的放 docstring 里。

## 代码配方

4. **纯语法用可运行 `.py` + `print` 展示** —— 每个文件能直接 `python xx.py` 跑,
   打印出运行结果一目了然(不用 `assert`);报错分支用 `SystemExit` 捕获后打印说明,不让程序中断。
5. **打印展示要直观** —— 结果逐字段打印,并带上类型:`print("  x:", x, type(x))`;
   不要一行 dump 整个对象;多个用例用 `① ② ③` 小标题分隔。
6. **`if __name__ == "__main__":` 里只放调用** —— 每段演示封装成 `demo序号_xxx()` 函数
   (如 `demo01_basic()` / `demo02_types()`),序号对应 docstring 里的 ① ② ③;
   主块只剩一串调用,实现都写在上面。
7. **换行看语义,不为拆而拆** —— 只有"命令行参数列表"(模拟 argv 的字符串序列,
   如 `parse_args(["input.txt", "-o", "out.txt"])`)才一行一参数地拆开、体现"这是命令行";
   **普通函数的关键字参数一行写完**(如 `df.to_parquet(path, engine="pyarrow", compression="snappy")`)。
8. **demo 产出写到脚本旁 `data/` 目录**(已被 `.gitignore` 忽略),不用 `tempfile`。
9. **文件顶部注释写清**:所属标准库/三方库、Python 版本、运行或安装方式。
10. **注释和 docstring 一律用中文**。
11. **给的 demo 必须是可执行的**,写完实际跑一遍确认输出正常再算完成。

## 命名

12. **项目名 `pycookbook`**(不是 python-cookbook)。
13. **别把顶层命名为 `python` 或 `test`** —— 会和解释器概念、pytest/标准库 `test` 混淆。

## Git 提交信息

格式：`<type>(<scope>): <描述>`

- **scope** 可选，填改动所在的库/模块名，如 `argparse`、`parquet`、`numpy`。
- **描述**用中文，动词开头，不加句号，首行不超过 72 字。
- **正文**（body）可选，空行隔开，一两句说清楚"为什么"即可，不要复述"改了什么"。

| type | 含义 | 例子 |
|------|------|------|
| **feat** | 新功能，用户能感知的新能力 | `feat(argparse): 新增子命令示例` |
| **fix** | 修 bug | `fix(parquet): 修复压缩参数缺失` |
| docs | 只改文档、注释、README | `docs: 补充目录设计说明` |
| style | 格式、空格，不改逻辑 | `style: 统一 type 打印格式` |
| **refactor** | 重构，既不加功能也不修 bug | `refactor(argparse): 拆分 demo 函数` |
| **perf** | 性能优化，功能不变 | `perf(parquet): 换用 snappy 压缩` |
| test | 加/改测试代码 | `test: 补全 argparse 边界用例` |
| build | 改构建系统、依赖 | `build: 升级 pyarrow 至 16.x` |
| ci | 改 CI 流水线 | `ci: 新增 Windows 测试 job` |
| **chore** | 杂务，不动 src 和测试 | `chore: 删除旧目录设计文档` |
| revert | 回滚某次提交 | `revert: revert "feat: xxx"` |

加粗为高频 type，其余按需使用。

**工作方式**：提交说明由 Claude 生成文字，实际 `git commit` 由用户执行。

---

> 新习惯确立后追加到这里,保持一句话一条、可执行、不啰嗦。
