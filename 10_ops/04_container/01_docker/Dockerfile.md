# Dockerfile 用法

## 指令速查

```dockerfile
FROM python:3.12-slim          # 基础镜像（必须是第一条指令）
                               # slim = 精简版，去掉了调试工具，体积约 130MB（完整版 ~1GB）
                               # alpine = 极简版，基于 musl libc，约 20MB，但兼容性有坑

WORKDIR /app                   # 设置工作目录，不存在会自动创建
                               # 后续 COPY/RUN/CMD 都在此目录执行，等价于 cd /app

COPY requirements.txt .        # 复制文件：COPY <宿主机路径> <容器路径>
                               # . 表示当前 WORKDIR（/app）
COPY . .                       # 复制整个目录（受 .dockerignore 过滤）
COPY --chown=1000:1000 . .     # 复制并指定文件所有者（uid:gid）

ADD src.tar.gz /app/           # ADD 比 COPY 多两个能力：
                               # 1. 自动解压 .tar.gz
                               # 2. 支持 URL 下载
                               # 其余场景一律用 COPY，语义更明确

RUN pip install -r requirements.txt          # 在构建时执行命令，结果固化为新层
RUN apt-get update && apt-get install -y \   # 多条命令用 && 连接，合并为一层，减小镜像体积
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*           # 清理 apt 缓存，否则缓存也会打进镜像

ENV APP_ENV=production         # 设置环境变量，容器运行时可见
ENV PATH="/app/bin:$PATH"      # 追加 PATH

ARG VERSION=1.0                # 构建时参数：docker build --build-arg VERSION=2.0 .
                               # ARG 只在构建阶段可见，不会写入最终镜像（不同于 ENV）

EXPOSE 8000                    # 声明容器监听的端口（仅文档作用，不会自动映射）
                               # 需配合 docker run -p 8000:8000 才能从宿主机访问

VOLUME ["/data"]               # 声明挂载点（推荐用 docker run -v 或 compose volumes 替代）

USER 1000                      # 切换运行用户（uid），避免以 root 运行容器（安全实践）
USER appuser                   # 也可用用户名（需提前 RUN useradd 创建）

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
                               # 健康检查：docker ps 会显示 healthy/unhealthy
                               # compose 的 depends_on condition: service_healthy 依赖它

ENTRYPOINT ["python"]          # 容器入口，固定不变，docker run 的参数会追加到后面
CMD ["app.py"]                 # 默认参数，可被 docker run 后面的命令覆盖
                               # ENTRYPOINT + CMD 组合：python app.py
                               # docker run myapp other.py → 变成：python other.py

# 只用 CMD（更灵活）：
CMD ["python", "app.py"]       # docker run --rm myapp 会执行 python app.py
                               # docker run --rm myapp bash 会执行 bash

LABEL version="1.0" \          # 给镜像打元数据标签
      maintainer="me@example.com"
```

---

## 最佳实践：利用层缓存

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# ✅ 先复制依赖文件，单独安装
# 依赖不变时，这一层命中缓存，不重新安装（构建快很多）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ 再复制代码（代码经常变，放最后）
COPY . .

CMD ["python", "app.py"]
```

```dockerfile
# ❌ 错误示范：代码变动就重新安装所有依赖
FROM python:3.12-slim
WORKDIR /app
COPY . .                       # 代码一变，下面的 pip install 就失效缓存
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

---

## 多阶段构建（减小最终镜像）

```dockerfile
# 阶段一：构建（含编译工具，体积大）
FROM python:3.12 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt   # 安装到指定目录

# 阶段二：运行（只含运行时，体积小）
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /install /usr/local    # 只从 builder 阶段复制安装好的包
COPY . .
USER 1000
CMD ["python", "app.py"]
```

---

## Python 项目典型 Dockerfile

```dockerfile
FROM python:3.12-slim

# 安装系统依赖（如有）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 创建非 root 用户
RUN useradd -m -u 1000 appuser

# 安装 Python 依赖（利用层缓存）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY --chown=appuser:appuser . .

# 切换到非 root 用户
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["gunicorn", "app:app", "-w", "4", "-b", "0.0.0.0:8000"]
```

---

## .dockerignore（构建上下文过滤）

```
# .dockerignore —— 排除不需要打包进镜像的文件，加快构建、减小体积

.git
.gitignore
__pycache__
*.pyc
*.pyo
.pytest_cache
.venv
venv
.env                 # 敏感信息不打包进镜像！
*.log
data/
tests/
README.md
Dockerfile
docker-compose*.yml
```

---

## 常用基础镜像选型

```text
镜像                   大小       适用场景
-------------------    -------    ---------------------------
python:3.12            ~1GB       开发调试，含完整工具链
python:3.12-slim       ~130MB     生产首选，去掉了多余工具
python:3.12-alpine     ~50MB      极致精简，但 musl libc 有兼容性坑
ubuntu:22.04           ~80MB      需要 apt 装系统库时用
debian:bookworm-slim   ~75MB      兼容性好的精简 Debian
```

---

## 构建与调试

```bash
# 构建
docker build -t myapp:latest .
docker build -t myapp:1.0 --build-arg VERSION=1.0 .

# 查看镜像分层（分析哪一层最大）
docker history myapp:latest

# 进入镜像调试（不启动应用）
docker run --rm -it myapp:latest bash

# 只执行到某个阶段（多阶段构建调试）
docker build --target builder -t myapp:debug .
```
