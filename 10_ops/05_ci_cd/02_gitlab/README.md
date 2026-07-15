# GitLab

私有化代码托管 + CI/CD 一体化平台，适合内网部署。

| 文件 | 内容 |
|------|------|
| [docker-compose.yml](docker-compose.yml) | Docker 部署配置（推荐方式） |
| [.gitlab-ci.yml](.gitlab-ci.yml) | CI/CD Pipeline 配置模板 |

---

## 部署

### Docker（推荐）

```bash
# 启动（首次启动需要 3~5 分钟初始化）
docker compose up -d

# 查看启动日志
docker logs -f gitlab

# 获取 root 初始密码（只在首次启动后 24 小时内有效）
docker exec gitlab cat /etc/gitlab/initial_root_password
```

浏览器打开 `http://localhost`，用 `root` + 上面的密码登录，**立即修改密码**。

---

### Linux（Ubuntu，apt 安装）

```bash
# 1. 安装依赖
sudo apt install -y curl openssh-server ca-certificates tzdata perl

# 2. 添加 GitLab 源
curl -sS https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh | sudo bash

# 3. 安装（EXTERNAL_URL 决定克隆地址前缀）
sudo EXTERNAL_URL="http://gitlab.example.com" apt install -y gitlab-ce

# 4. 初始密码
sudo cat /etc/gitlab/initial_root_password
```

常用管理命令：
```bash
sudo gitlab-ctl start            # 启动所有服务
sudo gitlab-ctl stop             # 停止
sudo gitlab-ctl restart          # 重启
sudo gitlab-ctl status           # 查看各组件状态
sudo gitlab-ctl reconfigure      # 修改 /etc/gitlab/gitlab.rb 后执行使配置生效
sudo gitlab-ctl tail             # 实时查看所有日志
```

---

### Windows

GitLab 官方**不支持** Windows 原生安装，Windows 下推荐用 Docker Desktop 运行上面的 docker-compose。

---

## 首次使用流程

```text
1. 登录 root 账号，修改密码
2. 管理员后台（Admin Area）→ 关闭注册（Settings → Sign-up restrictions）
3. 创建 Group（类似组织/命名空间）
4. Group 内创建 Project（代码仓库）
5. 本地配置 SSH Key 或 Personal Access Token
6. git clone / push 代码
```

---

## SSH Key 配置

```bash
# 生成 SSH Key（本地执行）
ssh-keygen -t ed25519 -C "your@email.com"

# 复制公钥
cat ~/.ssh/id_ed25519.pub

# GitLab → 右上角头像 → Preferences → SSH Keys → 粘贴公钥 → Add key

# 测试连接
ssh -T git@gitlab.example.com   # 成功会显示 Welcome to GitLab, @username!
```

---

## Personal Access Token（HTTP 方式）

```bash
# GitLab → 右上角头像 → Access Tokens → 创建 token（勾选 read_repository / write_repository）

# 克隆时使用
git clone http://oauth2:<TOKEN>@gitlab.example.com/group/project.git

# 或者配置 git credential
git config --global credential.helper store
# 首次 push 输入用户名（gitlab用户名）和密码（token），之后自动记住
```

---

## GitLab CI/CD 核心概念

```text
Pipeline     一次完整的 CI/CD 流程，由一个或多个 Stage 组成
Stage        阶段（install / test / build / deploy），同阶段的 Job 并行执行
Job          最小执行单元，在 Runner 上运行 script 里的命令
Runner       执行 Job 的代理进程，可以是 Docker 容器、物理机等
Artifact     Job 产生的文件，可传递给后续 Job 或供下载
Cache        跨 Pipeline 复用的文件（如 pip 缓存、node_modules）
Environment  部署环境（staging / production），可追踪部署历史
```

## 常用内置变量

```text
CI_COMMIT_SHA           完整 commit hash
CI_COMMIT_SHORT_SHA     短 hash（8位），常用作镜像 tag
CI_COMMIT_BRANCH        当前分支名
CI_PROJECT_NAME         项目名
CI_REGISTRY             GitLab Container Registry 地址
CI_REGISTRY_IMAGE       当前项目镜像地址
CI_REGISTRY_USER        Registry 登录用户名（内置，无需手动配）
CI_REGISTRY_PASSWORD    Registry 登录密码（内置）
CI_PIPELINE_ID          Pipeline ID
CI_JOB_ID               Job ID
```

## 注册 Runner（让 CI 有地方跑）

```bash
# Docker 方式注册 Runner
docker run --rm -it \
  -v /srv/gitlab-runner/config:/etc/gitlab-runner \
  gitlab/gitlab-runner register

# 按提示输入：
# URL: http://gitlab.example.com
# Token: 在 GitLab → Admin → Runners → Registration token
# Executor: docker
# Default image: python:3.12-slim
```

---

## 备份与恢复

```bash
# Docker 方式备份
docker exec gitlab gitlab-backup create

# 备份文件在容器内：/var/opt/gitlab/backups/
# 对应宿主机 volume：gitlab_data

# 恢复
docker exec gitlab gitlab-backup restore BACKUP=<时间戳>
```

---

## 资源需求参考

```text
规模         内存        CPU
---------    --------    -----
个人/小团队   4GB+        2核+
10~50人      8GB+        4核+
50人以上      16GB+       8核+

首次启动较慢（3~5分钟），完全启动后内存占用约 2~3GB。
```
