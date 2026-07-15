# Jenkins

老牌自托管 CI/CD 工具，插件生态丰富，适合内网/私有化部署场景。

| 文件 | 内容 |
|------|------|
| [docker-compose.yml](docker-compose.yml) | Docker 部署配置（推荐方式） |
| [Jenkinsfile](Jenkinsfile) | 声明式 Pipeline 最简模板 |

## 三种部署方式

### Docker（推荐）

```bash
# 启动
docker compose up -d

# 查看初始管理员密码
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword

# 浏览器打开
# http://localhost:8080
```

或者不用 compose，直接 docker run：

```bash
docker run -d \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  --name jenkins \
  jenkins/jenkins:lts
```

---

### Linux（Ubuntu）

```bash
# 1. 安装 Java（Jenkins 依赖 Java 17+）
sudo apt install -y openjdk-17-jdk

# 2. 添加 Jenkins APT 源
curl -fsSL https://pkg.jenkins.io/debian/jenkins.io-2023.key | sudo tee \
  /usr/share/keyrings/jenkins-keyring.asc > /dev/null
echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian binary/" | sudo tee \
  /etc/apt/sources.list.d/jenkins.list

# 3. 安装并启动
sudo apt update && sudo apt install -y jenkins
sudo systemctl enable jenkins && sudo systemctl start jenkins

# 4. 初始密码
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

---

### Windows

```powershell
# 1. 安装 JDK
winget install Microsoft.OpenJDK.17

# 2. 下载 jenkins.msi 安装包，双击安装
# https://www.jenkins.io/download/ → Windows

# 安装后自动注册为 Windows 服务，开机自启
# 初始密码位置：
# C:\ProgramData\Jenkins\.jenkins\secrets\initialAdminPassword
```

---

## 首次使用流程（三种部署通用）

```text
1. 浏览器打开 http://localhost:8080
2. 粘贴初始密码（位置见上方）
3. 安装推荐插件（等 2~5 分钟）
4. 创建管理员账号
5. 新建 Item → Pipeline → 关联 Git 仓库 → 写 Jenkinsfile
```

## 三种方式对比

```text
方式      优点                          缺点
-------   ----------------------------  ----------------------
Docker    隔离干净，一键启动，易迁移     需额外配置 Docker-in-Docker
Linux     生产主流，性能好               需手动配置 Java + 源
Windows   图形化安装简单                 环境依赖复杂，不易迁移
```

## 核心概念

```text
Pipeline    用 Groovy DSL（Jenkinsfile）描述的构建流程，放在项目根目录
Agent       执行任务的节点（本机 / Docker 容器 / Kubernetes Pod）
Stage       流水线的阶段（拉代码 / 测试 / 构建 / 部署）
Step        Stage 内的具体操作（sh / checkout / docker / junit）
Blue Ocean  可视化 Pipeline 插件（Jenkins 内安装）
```

## 常用内置变量

```groovy
BUILD_NUMBER   // 构建序号，每次自增
BUILD_URL      // 本次构建的 Web 链接
BRANCH_NAME    // 当前分支名
WORKSPACE      // Jenkins 工作目录路径
GIT_COMMIT     // 当前 commit hash
```
