# Docker Compose 常用命令与配置

## 常用命令

```bash
# 启停
docker compose up -d                     # 后台启动所有服务（-d = detached）
docker compose up -d --build             # 启动前强制重新构建镜像
docker compose down                      # 停止并删除容器、网络（保留卷）
docker compose down -v                   # 同上，额外删除卷（危险，会丢数据）
docker compose restart                   # 重启所有服务
docker compose restart web               # 只重启 web 服务

# 查看状态
docker compose ps                        # 列出服务状态
docker compose logs                      # 查看所有服务日志
docker compose logs -f web               # 实时跟踪 web 服务日志
docker compose logs --tail 50            # 只看最后 50 行

# 执行命令
docker compose exec web bash             # 进入 web 容器
docker compose exec web python manage.py migrate  # 在容器内执行命令
docker compose run --rm web pytest       # 临时启动一个容器执行命令，结束后删除

# 构建
docker compose build                     # 构建所有服务镜像
docker compose build web                 # 只构建 web 服务
docker compose pull                      # 拉取所有服务的最新镜像
```

## docker-compose.yml 结构

```yaml
services:              # 定义所有服务（容器）
  web:                 # 服务名，可自定义
    ...
  db:
    ...

volumes:               # 定义命名卷
  pgdata:

networks:              # 定义自定义网络（可选，不写则自动创建默认网络）
  backend:
```

## 完整示例：Web + 数据库 + Redis

```yaml
services:

  web:
    build: .                             # 用当前目录 Dockerfile 构建
    ports:
      - "8000:8000"                      # 宿主机:容器
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
      - REDIS_URL=redis://redis:6379
    env_file:
      - .env                             # 从 .env 文件批量注入（敏感信息不写进 yml）
    volumes:
      - .:/app                           # 挂载代码目录（开发时热更新）
    depends_on:
      db:
        condition: service_healthy       # 等 db 健康检查通过再启动
      redis:
        condition: service_started
    restart: unless-stopped

  db:
    image: postgres:16
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      - pgdata:/var/lib/postgresql/data  # 命名卷持久化数据库数据
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine                # alpine = 极简版，体积小
    volumes:
      - redisdata:/data

volumes:
  pgdata:                                # Docker 管理的命名卷，宿主机路径由 Docker 决定
  redisdata:
```

## 多环境配置（override 模式）

```bash
# 开发环境（默认）
docker compose up -d
# 等价于：docker compose -f docker-compose.yml -f docker-compose.override.yml up -d

# 生产环境
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

```yaml
# docker-compose.override.yml（开发环境覆盖，自动加载）
services:
  web:
    volumes:
      - .:/app                           # 开发时挂载代码，生产不需要
    command: python manage.py runserver  # 开发时用 runserver
```

```yaml
# docker-compose.prod.yml（生产环境覆盖）
services:
  web:
    command: gunicorn app:app -w 4       # 生产用 gunicorn
    restart: always
```

## 常用配置项速查

```text
配置项                  含义
--------------------    ------------------------------------------
image                   使用现成镜像
build                   构建镜像（指定 Dockerfile 路径）
ports                   端口映射 宿主:容器
volumes                 挂载卷或目录
environment             设置环境变量（列表或字典）
env_file                从文件批量注入环境变量
depends_on              服务依赖顺序
restart                 重启策略（no / always / unless-stopped / on-failure）
networks                加入的网络
healthcheck             健康检查命令
command                 覆盖默认启动命令
entrypoint              覆盖默认入口点
deploy.replicas         副本数（Swarm 模式）
profiles                按场景选择性启动（如 profiles: [dev]）
```

## .env 文件（环境变量管理）

```bash
# .env（不提交到 git，加入 .gitignore）
POSTGRES_PASSWORD=secret123
SECRET_KEY=my-secret-key
DEBUG=false
```

```yaml
# docker-compose.yml 里引用
services:
  web:
    environment:
      - SECRET_KEY=${SECRET_KEY}         # 从 .env 读取
      - DEBUG=${DEBUG}
```
