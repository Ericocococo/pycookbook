# Docker

| 文件 | 内容 |
|------|------|
| [README.md](README.md) | 安装、重装、升级、常用命令、镜像加速、导入导出、docker cp、私有 Registry、日志驱动、资源限制、网络模式、多平台构建、Context、安全加固、常见问题排查、commit、diff、events、健康检查+重启策略 |
| [Dockerfile.md](Dockerfile.md) | 全指令说明、层缓存最佳实践、多阶段构建、Python 典型模板、.dockerignore |

## 安装

### Windows

```powershell
# 方式一：Docker Desktop（推荐，带图形界面）
winget install Docker.DockerDesktop
# 安装后重启，启动 Docker Desktop 即可

# 方式二：WSL2 + Docker Desktop
# 先启用 WSL2：
wsl --install
# 再装 Docker Desktop，Settings → Use WSL2 based engine 勾上
```

验证安装：
```powershell
docker version
docker run hello-world
```

### Linux

**第一步：查看操作系统版本**

```bash
cat /etc/os-release          # 查看发行版名称和版本号
uname -r                     # 查看内核版本
arch                         # 查看架构（x86_64 / aarch64）
```

输出示例：
```text
NAME="Ubuntu"
VERSION="22.04.3 LTS (Jammy Jellyfish)"
...
```

根据 `NAME` 字段选择对应的安装方式：

---

#### Ubuntu / Debian

```bash
# 1. 卸载旧版本（如有）
sudo apt remove docker docker-engine docker.io containerd runc

# 2. 安装依赖
sudo apt update
sudo apt install -y ca-certificates curl gnupg

# 3. 添加 Docker 官方 GPG Key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# 4. 添加 Docker APT 源
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list

# 5. 安装
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io \
    docker-buildx-plugin docker-compose-plugin

# ── 或者用官方一键脚本（以上步骤的简化版）──
curl -fsSL https://get.docker.com | sh
```

---

#### CentOS / RHEL / Rocky Linux

```bash
# 1. 卸载旧版本（如有）
sudo yum remove docker docker-client docker-client-latest \
    docker-common docker-latest docker-engine

# 2. 安装 yum-utils
sudo yum install -y yum-utils

# 3. 添加 Docker YUM 源
sudo yum-config-manager --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

# 4. 安装
sudo yum install -y docker-ce docker-ce-cli containerd.io \
    docker-buildx-plugin docker-compose-plugin

# CentOS 8+ / Rocky Linux 用 dnf 替代 yum：
# sudo dnf install -y docker-ce docker-ce-cli containerd.io \
#     docker-buildx-plugin docker-compose-plugin
```

---

**安装后通用步骤（Ubuntu / CentOS 都要做）：**

```bash
# 启动并设置开机自启
sudo systemctl enable docker
sudo systemctl start docker

# 把当前用户加入 docker 组（避免每次 sudo）
sudo usermod -aG docker $USER
newgrp docker        # 立即生效；或者重新登录 SSH

# 验证
docker version
docker run hello-world
```

### 安装 Docker Compose（Linux 独立安装）

```bash
# Docker Desktop（Win/Mac）已内置 compose，Linux 需单独装
sudo apt install -y docker-compose-plugin   # Ubuntu 22.04+

# 验证
docker compose version
```

---

## 重新安装 / 卸载

### Windows

```powershell
# 1. 卸载 Docker Desktop
winget uninstall Docker.DockerDesktop

# 2. 清理残留数据（可选，彻底清干净）
Remove-Item -Recurse -Force "$env:APPDATA\Docker"
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\Docker"
Remove-Item -Recurse -Force "$env:PROGRAMDATA\Docker"

# 3. 重新安装
winget install Docker.DockerDesktop
```

### Linux

#### Ubuntu / Debian

```bash
# 1. 停止服务
sudo systemctl stop docker

# 2. 卸载所有 Docker 相关包
sudo apt remove -y docker-ce docker-ce-cli containerd.io \
    docker-buildx-plugin docker-compose-plugin

# 3. 清理残留数据（镜像、容器、卷全删）
sudo rm -rf /var/lib/docker
sudo rm -rf /var/lib/containerd
sudo rm -f /etc/apt/sources.list.d/docker.list
sudo rm -f /etc/apt/keyrings/docker.gpg

# 4. 重新安装
curl -fsSL https://get.docker.com | sh

# 5. 把用户加回 docker 组
sudo usermod -aG docker $USER
newgrp docker
```

#### CentOS / RHEL / Rocky Linux

```bash
# 1. 停止服务
sudo systemctl stop docker

# 2. 卸载
sudo yum remove -y docker-ce docker-ce-cli containerd.io \
    docker-buildx-plugin docker-compose-plugin

# 3. 清理残留数据
sudo rm -rf /var/lib/docker
sudo rm -rf /var/lib/containerd

# 4. 重新安装
sudo yum install -y docker-ce docker-ce-cli containerd.io \
    docker-buildx-plugin docker-compose-plugin

# 5. 启动并加用户组
sudo systemctl enable docker && sudo systemctl start docker
sudo usermod -aG docker $USER && newgrp docker
```

### 只重置数据、不重装

```bash
# 删除所有容器、镜像、卷、网络（慎用，不可恢复）
docker system prune -a --volumes

# 重启 Docker 服务
sudo systemctl restart docker          # Linux
# Windows：任务栏 Docker 图标 → Restart Docker Desktop
```

**场景速查：**

```text
场景                         操作
--------------------------   ----------------------------------
环境出问题，清数据重来         docker system prune -a --volumes
版本太旧，想升级               apt upgrade docker-ce / winget upgrade
彻底重装（驱动/配置出问题）     卸载 → 删残留 → 重装
```

---

## 镜像

```bash
docker images                            # 列出本地所有镜像
docker pull nginx:latest                 # 从 Docker Hub 拉取镜像
docker build -t myapp:1.0 .              # 用当前目录 Dockerfile 构建镜像，-t 指定名称:标签
docker build -t myapp:1.0 -f path/Dockerfile .  # 指定 Dockerfile 路径
docker rmi myapp:1.0                     # 删除镜像
docker image prune                       # 清理悬空镜像（没有标签、没有容器引用的）
docker image prune -a                    # 清理所有未被容器使用的镜像
```

## 容器生命周期

```bash
# 运行
docker run -d -p 8080:80 --name web nginx       # 后台运行，端口映射 宿主:容器，命名
docker run -it ubuntu bash                       # 交互式运行，进入 bash
docker run --rm -it python:3.12 python           # 退出后自动删除容器

# 启停
docker start web                                 # 启动已停止的容器
docker stop web                                  # 优雅停止（发 SIGTERM，等 10s 再 SIGKILL）
docker restart web                               # 重启
docker kill web                                  # 立即强制停止（SIGKILL）

# 删除
docker rm web                                    # 删除已停止的容器
docker rm -f web                                 # 强制删除（运行中也删）
docker container prune                           # 删除所有已停止的容器
```

## 查看状态

```bash
docker ps                                # 列出运行中的容器
docker ps -a                             # 列出所有容器（含已停止）
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"  # 自定义列

docker logs web                          # 查看容器日志
docker logs -f web                       # 实时跟踪日志（follow）
docker logs --tail 100 web               # 只看最后 100 行
docker logs --since 10m web              # 只看最近 10 分钟的日志

docker inspect web                       # 容器详细信息（JSON），含 IP、挂载、环境变量等
docker stats                             # 实时资源占用（CPU、内存、网络）
docker stats --no-stream                 # 只看当前快照，不持续刷新
docker top web                           # 查看容器内进程
```

## 进入容器

```bash
docker exec -it web bash                 # 进入运行中的容器，开启交互式 bash
docker exec -it web sh                   # bash 不存在时用 sh（alpine 镜像常见）
docker exec web cat /etc/hosts           # 在容器内执行单条命令，不进入交互
docker exec -e FOO=bar web env           # 临时传入环境变量执行命令
```

## 数据卷

```bash
docker volume ls                         # 列出所有卷
docker volume create mydata              # 创建命名卷
docker volume inspect mydata             # 查看卷详情（存储路径等）
docker volume rm mydata                  # 删除卷
docker volume prune                      # 删除所有未使用的卷

# 挂载方式
docker run -v mydata:/data nginx         # 命名卷（Docker 管理，推荐持久化数据）
docker run -v /host/path:/container/path nginx   # 绑定挂载（宿主机目录，推荐开发调试）
docker run --mount type=tmpfs,target=/tmp nginx  # tmpfs（内存，容器停止即消失）
```

## 网络

```bash
docker network ls                        # 列出所有网络
docker network create mynet              # 创建自定义桥接网络
docker network inspect mynet            # 查看网络详情
docker network connect mynet web         # 把运行中的容器加入网络
docker run --network mynet nginx         # 启动时指定网络

# 同一自定义网络内的容器可以用容器名互相访问（DNS 自动解析）
# 例：web 容器可以 curl http://db:5432 访问同网络的 db 容器
```

## 清理

```bash
docker system prune                      # 清理停止的容器 + 悬空镜像 + 无用网络
docker system prune -a                   # 额外清理未被任何容器使用的镜像
docker system prune -a --volumes         # 连卷一起清理（危险，会丢数据）
docker system df                         # 查看 Docker 磁盘占用明细
```

## run 参数速查

```text
参数                     含义
---------------------    ------------------------------------------
-d                       后台运行（detached）
-it                      交互式终端（-i 保持 stdin，-t 分配 TTY）
-p 8080:80               端口映射 宿主机端口:容器端口
-v /host:/container      挂载目录或卷
--name web               给容器命名
--rm                     退出后自动删除容器
-e KEY=VAL               设置环境变量
--env-file .env          从文件批量注入环境变量
--network mynet          指定网络
--restart unless-stopped 重启策略（always / on-failure / unless-stopped）
--cpus 1.5               限制 CPU 核数
--memory 512m            限制内存
-u 1000:1000             指定运行用户（uid:gid）
```

## Dockerfile 速查

```dockerfile
FROM python:3.12-slim          # 基础镜像，slim = 精简版，体积小
WORKDIR /app                   # 设置工作目录，后续命令都在此目录执行
COPY requirements.txt .        # 先只复制依赖文件，利用层缓存
RUN pip install -r requirements.txt  # 安装依赖（单独一层，代码变动时不重新安装）
COPY . .                       # 再复制全部代码
EXPOSE 8000                    # 声明容器监听的端口（文档用，不会自动映射）
ENV APP_ENV=production         # 设置环境变量
CMD ["python", "app.py"]       # 容器启动命令（ENTRYPOINT 固定命令，CMD 提供默认参数）
```

---

## 镜像加速（国内必备）

Docker Hub 在国内访问慢，配置镜像加速器可显著提速。

### Linux

```bash
# 编辑（没有则新建）Docker daemon 配置文件
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<EOF
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
EOF

# 重启 Docker 使配置生效
sudo systemctl daemon-reload
sudo systemctl restart docker

# 验证配置是否生效
docker info | grep -A 5 "Registry Mirrors"
```

### Windows（Docker Desktop）

```text
Docker Desktop → Settings → Docker Engine → 编辑 JSON，加入：

{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://docker.mirrors.ustc.edu.cn"
  ]
}

→ Apply & Restart
```

### 常用镜像加速地址

```text
腾讯云（推荐）    https://mirror.ccs.tencentyun.com
中科大           https://docker.mirrors.ustc.edu.cn
网易             https://hub-mirror.c.163.com
阿里云           https://[你的ID].mirror.aliyuncs.com   （需登录阿里云控制台获取专属地址）
```

---

## 镜像导入导出（离线迁移）

适用场景：内网服务器无法联网，把镜像打包后通过 U 盘 / scp 传输。

```bash
# 导出镜像为 tar 文件
docker save -o myapp.tar myapp:1.0              # 单个镜像
docker save -o images.tar myapp:1.0 nginx:latest  # 多个镜像打包到一个文件

# 压缩（体积可减少 50%~70%）
docker save myapp:1.0 | gzip > myapp.tar.gz

# 导入
docker load -i myapp.tar                        # 从 tar 文件导入
docker load -i myapp.tar.gz                     # 支持直接读 gzip 压缩文件
gunzip -c myapp.tar.gz | docker load            # 等价写法

# 查看导入结果
docker images

# 传输到远程服务器再导入
scp myapp.tar.gz user@server:/tmp/
ssh user@server "docker load -i /tmp/myapp.tar.gz"
```

**save vs export 的区别：**

```text
docker save    → 导出镜像（含所有层和历史），用于镜像迁移
docker export  → 导出容器文件系统快照（丢失历史和元数据），体积更小
docker load    → 对应 save 的导入
docker import  → 对应 export 的导入
```

---

## docker cp（容器 ↔ 宿主机 拷贝文件）

```bash
# 宿主机 → 容器
docker cp ./config.yml web:/app/config.yml       # 拷贝单文件
docker cp ./static/ web:/app/static/             # 拷贝整个目录

# 容器 → 宿主机
docker cp web:/app/logs/app.log ./app.log        # 从容器取出日志
docker cp web:/app/data/ ./backup/               # 取出整个目录

# 容器不需要运行，停止状态也可以 cp
docker cp stopped_container:/etc/config.yml .
```

---

## 私有 Registry

### 使用 GitLab / Harbor Registry

```bash
# 登录私有 Registry
docker login registry.example.com               # 按提示输入用户名和密码
docker login registry.example.com -u user -p token  # 非交互式（CI 脚本用）

# 给本地镜像打 tag（格式：registry地址/命名空间/镜像名:标签）
docker tag myapp:1.0 registry.example.com/mygroup/myapp:1.0

# 推送
docker push registry.example.com/mygroup/myapp:1.0

# 拉取
docker pull registry.example.com/mygroup/myapp:1.0

# 退出登录
docker logout registry.example.com
```

### 搭建本地 Registry（轻量，无 UI）

```bash
# 启动官方 registry 容器
docker run -d \
  -p 5000:5000 \
  --name registry \
  -v registry_data:/var/lib/registry \
  registry:2

# 推送到本地 registry
docker tag myapp:1.0 localhost:5000/myapp:1.0
docker push localhost:5000/myapp:1.0

# 拉取
docker pull localhost:5000/myapp:1.0

# 查看仓库内的镜像列表（REST API）
curl http://localhost:5000/v2/_catalog
curl http://localhost:5000/v2/myapp/tags/list
```

---

## 日志驱动

Docker 默认用 `json-file` 驱动，日志文件不限大小会撑满磁盘，**生产环境必须配置轮转**。

### 全局配置（所有容器生效）

```bash
# /etc/docker/daemon.json
sudo tee /etc/docker/daemon.json <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",    # 单个日志文件最大 100MB
    "max-file": "3"        # 最多保留 3 个轮转文件，即最多 300MB
  }
}
EOF
sudo systemctl restart docker
```

### 单个容器配置

```bash
docker run -d \
  --log-driver json-file \
  --log-opt max-size=50m \
  --log-opt max-file=5 \
  --name web nginx
```

### 常用日志驱动

```text
驱动          说明
-----------   ------------------------------------------
json-file     默认，日志存本地 JSON 文件，支持 docker logs 查看
syslog        发送到系统 syslog（/var/log/syslog）
journald      发送到 systemd journal，用 journalctl 查看
none          禁用日志，docker logs 不可用
fluentd       发送到 Fluentd（日志聚合平台）
awslogs       发送到 AWS CloudWatch
```

---

## 资源限制

### 运行时限制

```bash
docker run -d \
  --cpus 1.5 \           # 最多使用 1.5 个 CPU 核（可以是小数）
  --cpu-shares 512 \     # CPU 相对权重（默认 1024，竞争时按比例分配）
  --memory 512m \        # 内存上限 512MB，超出触发 OOM Kill
  --memory-swap 1g \     # 内存 + Swap 总上限（设成和 memory 相同 = 禁用 swap）
  --memory-reservation 256m \  # 软限制，内存紧张时回收到此值
  --pids-limit 100 \     # 容器内最多 100 个进程（防 fork bomb）
  --name web nginx

# 查看实时资源占用
docker stats web
docker stats --no-stream   # 只看当前快照
```

### 查看容器资源限制

```bash
docker inspect web | grep -A 20 '"HostConfig"'   # 查看完整资源配置
docker inspect web --format '{{.HostConfig.Memory}}'   # 只看内存限制（单位字节）
```

### OOM（内存不足）排查

```bash
# 容器被 OOM Kill 后会自动退出，状态码是 137
docker ps -a | grep Exited

# 查看内核 OOM 日志
dmesg | grep -i "oom\|killed"
journalctl -k | grep -i "oom\|killed"

# 预防：设置合理的内存上限，避免影响宿主机
docker run --memory 512m --memory-swap 512m ...   # 完全禁用 swap
```

---

## 升级 Docker

### Linux（Ubuntu / Debian）

```bash
# 查看当前版本
docker version

# 查看可用版本
apt-cache madison docker-ce

# 升级到最新版
sudo apt update
sudo apt upgrade -y docker-ce docker-ce-cli containerd.io \
    docker-buildx-plugin docker-compose-plugin

# 升级到指定版本
sudo apt install -y docker-ce=<VERSION_STRING>
```

### Linux（CentOS / Rocky）

```bash
# 查看可用版本
yum list docker-ce --showduplicates | sort -r

# 升级到最新
sudo yum update -y docker-ce docker-ce-cli containerd.io \
    docker-buildx-plugin docker-compose-plugin

# 升级到指定版本
sudo yum install -y docker-ce-<VERSION>
```

### Windows

```powershell
# 升级 Docker Desktop
winget upgrade Docker.DockerDesktop
```

---

## 网络模式详解

```bash
docker network ls    # 默认有三个网络：bridge / host / none
```

### bridge（默认）

```bash
# 容器连接到虚拟网桥 docker0，通过 NAT 访问外网
# 容器间通过 IP 互访，同一自定义桥接网络内可用容器名互访（DNS 解析）

docker run -d --name web nginx                    # 默认连接 bridge 网络
docker run -d --network mybridge --name web nginx  # 指定自定义桥接网络（推荐）

# 自定义桥接网络 vs 默认 bridge：
# 默认 bridge：容器间只能用 IP 互访，不能用容器名
# 自定义 bridge：容器间可以用容器名互访（有 DNS），推荐生产使用
docker network create mybridge
```

### host

```bash
# 容器直接使用宿主机网络栈，没有网络隔离
# 性能最好（无 NAT 开销），但端口直接暴露在宿主机上
docker run -d --network host nginx    # nginx 监听宿主机的 80 端口
# 注意：host 模式在 Docker Desktop（Win/Mac）上不生效，仅 Linux 有效
```

### none

```bash
# 容器没有网络接口，完全隔离
# 适合不需要网络的批处理任务
docker run --rm --network none alpine ip addr    # 只有 lo 回环接口
```

### overlay（Swarm / 跨主机）

```bash
# 跨多台宿主机的容器互联，需要 Swarm 模式
# 单机 Docker 用 bridge 即可，集群场景用 overlay 或 Kubernetes
docker network create -d overlay myoverlay
```

### 网络模式对比

```text
模式       隔离性    性能    适用场景
-------    ------    ----    ---------------------------
bridge     有        中      默认，单机多容器互联
host       无        高      需要最高网络性能，Linux 专属
none       完全隔离  -       无网络需求的任务
overlay    有        中      Swarm 集群跨主机通信
```

---

## 多平台构建（buildx）

适用场景：M 芯片 Mac 本地开发，部署到 x86 Linux 服务器；或同时发布 amd64 + arm64 镜像。

```bash
# 查看当前 builder
docker buildx ls

# 创建支持多平台的 builder（使用 QEMU 模拟）
docker buildx create --name multibuilder --use
docker buildx inspect --bootstrap    # 启动并检查 builder

# 构建多平台镜像并直接推送到 Registry
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t registry.example.com/myapp:1.0 \
  --push \
  .

# 只构建本地平台（不推送，加载到本地 docker images）
docker buildx build --platform linux/amd64 -t myapp:amd64 --load .

# 查看镜像支持的平台
docker buildx imagetools inspect registry.example.com/myapp:1.0
```

**注意：** `--push` 和 `--load` 不能同时用；多平台镜像必须推送到 Registry，不能直接 load 到本地。

---

## Docker Context（远程管理多台主机）

不用 SSH 登录远程服务器，直接在本地用 docker 命令管理远程 Docker。

```bash
# 查看当前所有 context
docker context ls

# 创建远程主机的 context（通过 SSH）
docker context create remote-server \
  --docker "host=ssh://user@192.168.1.100"

# 切换到远程 context（后续所有 docker 命令都在远程执行）
docker context use remote-server

# 验证：列出远程服务器上的容器
docker ps

# 切回本地
docker context use default

# 不切换 context，临时在远程执行单条命令
docker --context remote-server ps
docker --context remote-server compose up -d
```

---

## 安全加固

### 非 root 用户运行

```bash
# 运行时指定用户（uid:gid）
docker run -u 1000:1000 myapp

# Dockerfile 里切换用户（推荐）
RUN useradd -m -u 1000 appuser
USER appuser
```

### 只读文件系统

```bash
# --read-only：容器根文件系统只读，防止容器内写入恶意文件
docker run --read-only \
  --tmpfs /tmp \           # 临时目录仍可写（内存）
  --tmpfs /var/run \
  nginx
```

### 禁止特权模式

```bash
# 不要用 --privileged（赋予容器几乎等同于 root 的宿主机权限）
# 确实需要某项能力时，用 --cap-add 精细授权
docker run --cap-drop ALL \           # 先去掉所有 capability
  --cap-add NET_BIND_SERVICE \        # 只加回需要的（绑定 <1024 端口）
  nginx
```

### 常用安全参数

```text
参数                          含义
--------------------------    ------------------------------------------
--read-only                   根文件系统只读
--no-new-privileges           禁止容器内进程提权（sudo / setuid）
--cap-drop ALL                去掉所有 Linux capabilities
--cap-add <CAP>               精细添加单个 capability
--security-opt no-new-privileges  等价 --no-new-privileges
--user 1000:1000              非 root 用户运行
--pid host                    共享宿主机 PID 命名空间（慎用）
```

---

## 常见问题排查

### 容器启动失败

```bash
# 查看退出状态和原因
docker ps -a                            # 查看状态码
docker logs <容器名>                    # 查看启动日志，通常有明确报错
docker inspect <容器名> | grep -A5 '"State"'   # 查看详细退出信息

# 常见状态码
# 0   正常退出
# 1   程序内部错误
# 137 OOM Kill 或 docker kill（128 + 9）
# 139 段错误（128 + 11）
# 143 优雅终止 SIGTERM（128 + 15）
```

### 端口冲突

```bash
# 报错：Bind for 0.0.0.0:8080 failed: port is already allocated
# 查看宿主机端口占用
sudo ss -tlnp | grep 8080       # Linux
netstat -ano | findstr 8080     # Windows

# 找出占用端口的容器
docker ps --format "table {{.Names}}\t{{.Ports}}" | grep 8080
```

### 网络不通

```bash
# 容器内测试网络
docker exec web ping google.com           # 测试外网
docker exec web curl http://db:5432       # 测试容器间（需在同一网络）

# 检查容器是否在同一网络
docker network inspect mybridge           # 查看网络内的容器列表
docker inspect web --format '{{json .NetworkSettings.Networks}}'

# 容器加入网络
docker network connect mybridge web
```

### 磁盘空间不足

```bash
# 查看 Docker 磁盘占用
docker system df

# 按大小排列镜像
docker images --format "{{.Size}}\t{{.Repository}}:{{.Tag}}" | sort -rh | head -10

# 清理（按需选择）
docker container prune       # 删除已停止容器
docker image prune           # 删除悬空镜像
docker volume prune          # 删除未使用的卷
docker system prune -a       # 清理所有未使用资源（不含卷）
docker system prune -a --volumes   # 连卷一起清（危险）
```

### 权限问题

```bash
# 报错：Got permission denied while trying to connect to the Docker daemon socket
# 原因：当前用户不在 docker 组
sudo usermod -aG docker $USER
newgrp docker    # 立即生效，或重新登录

# 文件挂载权限问题：容器内无法写入挂载目录
# 原因：容器内用户 uid 与宿主机目录所有者不匹配
ls -la /host/path                        # 查看宿主机目录权限
docker run -u $(id -u):$(id -g) ...      # 用宿主机当前用户运行容器
# 或在 Dockerfile 里 chown：
# COPY --chown=1000:1000 . .
```

---

## docker commit（从容器创建镜像）

适用场景：在容器内手动调试安装了某些东西，想把当前状态保存为镜像。
**不推荐生产使用**（无法追溯变更，应用 Dockerfile 替代）。

```bash
# 进入容器手动安装
docker run -it ubuntu bash
# 容器内：apt install -y curl vim

# 退出后把当前容器状态保存为新镜像
docker commit <容器ID或名称> myubuntu:with-tools
# docker commit 容器名 镜像名:标签

# 查看生成的镜像
docker images myubuntu

# 可加 -m 写提交说明，-a 写作者
docker commit -m "安装了 curl 和 vim" -a "me" <容器ID> myubuntu:with-tools
```

---

## docker diff（查看容器文件变更）

查看容器相对基础镜像的文件系统变更，排查容器内改了哪些文件。

```bash
docker diff <容器名>

# 输出格式：
# A /path  → Added，新增文件
# C /path  → Changed，修改文件
# D /path  → Deleted，删除文件

# 示例输出：
# C /etc
# A /etc/curl.conf
# C /var/log
# A /var/log/app.log
```

---

## docker events（实时监听 Docker 事件）

监听 Docker daemon 产生的事件流，适合调试、监控、自动化触发。

```bash
# 实时监听所有事件
docker events

# 只看容器相关事件
docker events --filter type=container

# 只看特定容器的事件
docker events --filter container=web

# 只看特定事件类型
docker events --filter event=start
docker events --filter event=stop
docker events --filter event=die      # 容器异常退出

# 查看过去 1 小时的历史事件
docker events --since 1h --until 0s

# 常见事件类型
# container: create / start / stop / kill / die / destroy / exec_start
# image:     pull / push / build / delete
# network:   connect / disconnect / create / destroy
# volume:    create / mount / unmount / destroy
```

---

## 健康检查 + 重启策略

### HEALTHCHECK（Dockerfile 里定义）

```dockerfile
# 每 30s 检查一次，超时 5s，连续失败 3 次才标记为 unhealthy
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
    # exit 0 = healthy，exit 1 = unhealthy
    # --start-period：容器启动后多久才开始计入失败次数（给服务启动时间）
```

```bash
# 查看健康状态
docker ps                              # STATUS 列显示 healthy / unhealthy / starting
docker inspect web --format '{{.State.Health.Status}}'   # 只看健康状态
docker inspect web --format '{{json .State.Health}}'     # 看完整健康检查历史
```

### 重启策略（--restart）

```bash
docker run --restart unless-stopped nginx    # 常用：除非手动停止，否则一直重启

# 四种策略：
# no（默认）       不自动重启
# always           总是重启（包括 docker 服务重启后）
# on-failure[:N]   仅在非 0 退出码时重启，可限制最多重试 N 次
# unless-stopped   除非手动 docker stop，否则一直重启（推荐生产使用）

# 结合健康检查：容器 unhealthy 不会自动触发重启，需要配合监控或 compose 的 condition
# compose 里可以用：
# deploy:
#   restart_policy:
#     condition: on-failure
#     max_attempts: 3
```
