# Pyright 企业级进阶 —— CI/CD、增量接入、Monorepo、性能调优

> 本章假设你已掌握 Pyright 基础（类型注解、配置、CLI），
> 聚焦**在真实项目中落地 Pyright** 会遇到的实际问题。

## 1. CI/CD 完整集成

### 1.1 GitHub Actions

```yaml
# .github/workflows/type-check.yml
name: Type Check

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  pyright:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
          npm install

      - name: Pyright check
        run: npx pyright --outputjson | jq -e '.summary.errorCount == 0'
```

### 1.2 GitLab CI

```yaml
# .gitlab-ci.yml
type-check:
  stage: test
  image: python:3.12
  before_script:
    - apt-get update && apt-get install -y nodejs npm jq
    - pip install -e ".[dev]"
    - npm install pyright
  script:
    - npx pyright --outputjson | jq -e '.summary.errorCount == 0'
```

### 1.3 Pre-commit 钩子

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/RobertCraigie/pyright-python
    rev: v1.1.411
    hooks:
      - id: pyright
        # 只在暂存区文件上运行（更快）
        args: ["--level", "error"]
```

```bash
pip install pre-commit
pre-commit install
```

### 1.4 仅检查 diff（增量 CI）

大型项目每次全量检查太慢，可以只检查 PR 改动的文件：

```bash
# 获取当前分支 vs main 的改动文件
git diff --name-only origin/main -- '*.py' | xargs pyright
```

### 1.5 `--outputjson` 解析示例

```python
"""CI 中解析 Pyright JSON 输出"""
import json
import subprocess
import sys

result = subprocess.run(
    ["pyright", "--outputjson", "src/"],
    capture_output=True, text=True,
)
report = json.loads(result.stdout)

summary = report["summary"]
errors = summary["errorCount"]
warnings = summary["warningCount"]

print(f"Errors: {errors}, Warnings: {warnings}")
if errors > 0:
    for d in report["generalDiagnostics"]:
        if d["severity"] == "error":
            print(f"  ❌ {d['file']}:{d['range']['start']['line']+1}")
            print(f"     {d['message']}")
    sys.exit(1)
```

## 2. 大型项目增量接入策略

### 2.1 四阶段方案

```
阶段 1: typeCheckingMode = "off"     → 不阻塞，只熟悉 CLI
阶段 2: typeCheckingMode = "basic"   + exclude 老代码
阶段 3: 逐模块开启 basic，关闭最吵的 report
阶段 4: typeCheckingMode = "strict"  + 全员通过
```

### 2.2 第一阶段：Off + 新代码先检

```json
{
  "typeCheckingMode": "off",
  "include": ["src/new_module"]
}
```

新模块强制类型注解，老代码不动。

### 2.3 第二阶段：Basic + 排除遗留

```json
{
  "typeCheckingMode": "basic",
  "include": ["src"],
  "exclude": [
    "src/legacy/**",
    "src/migrations/**",
    "**/test_*.py",
    "**/conftest.py"
  ],
  "reportMissingTypeStubs": "none",
  "reportUnknownMemberType": "none"
}
```

### 2.4 第三阶段：逐目录渗透

用 `executionEnvironments` 对不同目录设不同严格度：

```json
{
  "typeCheckingMode": "basic",
  "executionEnvironments": [
    {
      "root": "src/core",
      "typeCheckingMode": "strict"
    },
    {
      "root": "src/services",
      "typeCheckingMode": "basic",
      "reportOptionalMemberAccess": "error"
    },
    {
      "root": "src/legacy",
      "typeCheckingMode": "off"
    }
  ]
}
```

### 2.5 第四阶段：全员 Strict

```json
{
  "typeCheckingMode": "strict",
  "reportMissingTypeStubs": "warning",
  "reportUnknownMemberType": "error"
}
```

全员通过后，把 Pyright 作为 CI 阻断门。

### 2.6 逐步修复策略

```bash
# 1. 先看总共有多少问题
pyright --outputjson | jq '.summary'

# 2. 按严重度排序看
pyright --outputjson | jq '.generalDiagnostics | group_by(.severity)'

# 3. 统计最吵的规则
pyright --outputjson | jq '.generalDiagnostics | group_by(.rule) | map({rule: .[0].rule, count: length}) | sort_by(-.count)'

# 4. 先从 error 开始修，修完一个规则统一加 ignore
```

## 3. Monorepo 配置

### 3.1 每个包独立配置

```text
my-monorepo/
├── pyrightconfig.json          ← 根配置（宽松）
├── packages/
│   ├── shared/
│   │   ├── pyrightconfig.json  ← strict
│   │   └── src/
│   ├── backend/
│   │   └── pyrightconfig.json  ← basic
│   └── frontend/               ← 前端项目，不检查
```

根配置：

```json
{
  "typeCheckingMode": "basic",
  "exclude": ["packages/frontend/**"]
}
```

`packages/shared/pyrightconfig.json`：

```json
{
  "typeCheckingMode": "strict",
  "include": ["src"]
}
```

Pyright 会从被检查文件的目录向上查找，找到最近的 `pyrightconfig.json`。

### 3.2 共享类型包

包 A 导出类型，包 B 引用：

```json
// packages/b/pyrightconfig.json
{
  "typeCheckingMode": "basic",
  "extraPaths": [
    "../shared/src"
  ]
}
```

## 4. 性能调优

### 4.1 排除不必要的文件

```json
{
  "exclude": [
    "**/node_modules",
    "**/__pycache__",
    "**/.*",            // 所有隐藏目录
    "**/build/**",
    "**/dist/**",
    "**/tests/**",
    "**/vendor/**",
    "generated/**"
  ]
}
```

### 4.2 多线程

```json
{
  "typeCheckingMode": "basic",
  "include": ["src"]
}
```

```bash
# Pyright 默认自动使用多线程
# 也可以显式指定线程数：
pyright --threads 8
```

### 4.3 只检查改动文件

```bash
# 配合 git，只检查未提交的改动
git diff --name-only -- '*.py' | xargs pyright
```

### 4.4 避免 typeshed 重新解析

```bash
# Pyright 会缓存 typeshed 解析结果
# 如果缓存出问题，清掉重来：
rm -rf ~/.cache/pyright
```

### 4.5 诊断：Pyright 慢在哪

```bash
# --stats 输出性能统计
pyright --stats

# 输出示例：
#   Files analyzed: 1247
#   Time in parse: 2.3s
#   Time in bind: 1.1s
#   Time in check: 8.7s
#   Total time: 12.1s
```

如果 `Time in check` 过长，说明类型注解复杂的文件太多，考虑：

```json
{
  "reportExplicitAnyInPosition": "none",  // 关闭昂贵的检查
  "strictListInference": false,            // 关闭严格的列表推断
  "strictDictionaryInference": false
}
```

## 5. Pyright + Mypy 双检策略

### 5.1 为什么双检

| 场景 | Pyright 优势 | Mypy 优势 |
|------|-------------|-----------|
| 查出基本类型错误 | ✅ 更快 | ✅ 更全 |
| 装饰器类型推断 | ✅ 准确 | ⚠️ 有时误报 |
| `__init__` 返回值检查 | ❌ 不报 | ✅ 会报 |
| `self` / `cls` 类型 | ✅ 支持 | ✅ 支持 |
| Protocol 结构匹配 | ✅ 宽松 | ✅ 严格 |
| 代码量 | ✅ 可用 | ⚠️ 备选 |

### 5.2 双检 CI 配置

```yaml
type-check:
  stage: test
  script:
    # 先用 Pyright 快速检查（几秒到十几秒）
    - npx pyright src/
    # 再用 Mypy 做更深度的检查（可能需要几十秒）
    - mypy src/
```

### 5.3 双检配置共存

```json
// pyrightconfig.json
{
  "typeCheckingMode": "basic",
  "reportOptionalMemberAccess": "warning"
}
```

```ini
; mypy.ini
[mypy]
strict = true
ignore_missing_imports = true
```

同一段代码，两边都检，取各自擅长的结果。

## 6. pyproject.toml 配置

Pyright 支持在 `pyproject.toml` 的 `[tool.pyright]` 段写入配置：

```toml
[tool.pyright]
typeCheckingMode = "basic"
pythonVersion = "3.12"
pythonPlatform = "Windows"
include = ["src", "tests"]
exclude = ["src/legacy/**"]
reportOptionalMemberAccess = "warning"
reportUnusedVariable = "warning"
```

**注意**：如果同时存在 `pyrightconfig.json`，后者优先级更高。

## 7. 常见问题排查

```text
症状                        原因                                    解决
─────────────────────────   ────────────────────────────────────   ─────────────────
pyright 找不到三方库         venvPath / venv 没配                  检查 pyrightconfig.json
某库报很多 "Xxx is unknown"  该库没有类型，typeshed 也没有           加 stubs 或配置 reportMissingTypeStubs=none
检查结果和 VS Code 不一致    VS Code 用了不同的 Python 解释器或版本    检查 settings.json 的 pythonPath 与 pyrightconfig
pyright 突然变慢              缓存损坏                                rm -rf ~/.cache/pyright
pre-commit 报错与 CLI 不同   pre-commit 使用隔离环境                    检查 pre-commit 的 pyright 版本
```
