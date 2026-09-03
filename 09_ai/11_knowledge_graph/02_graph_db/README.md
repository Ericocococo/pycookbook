# 02_graph_db 图数据库 —— Neo4j

> Neo4j 是工业界最主流的图数据库，用**属性图**模型（节点/边都能带属性），
> Cypher 是它的查询语言。本目录先学 Cypher（语法不依赖服务器），再学连库操作。

| 文件 | 内容 |
|------|------|
| [01_cypher.md](01_cypher.md) | Cypher 语法速查：建节点/关系、查询、过滤、路径 |
| README.md | 安装 Neo4j + 从命令行跑 Cypher |

## 1. 知识点

### 1.1 为什么学 Neo4j

属性图 vs 01_basics 里的 RDF 图，两大流派对比：

| | 属性图（Neo4j） | RDF 图（语义网） |
|---|---|---|
| 模型 | 节点 + 关系 + 属性 | 全部三元组 |
| 查询语言 | Cypher | SPARQL |
| 生态 | 工业界主流（Neo4j/JanusGraph） | 学术界/开放数据（schema.org） |
| 上手难度 | 低，语法像 SQL | 高，全 URI 化 |

个人项目、工程系统用 Neo4j；要接开放知识库（Wikidata 等）再学 RDF。

### 1.2 安装 Neo4j

1. 装 Java：Neo4j 5.x 需要 **Java 17**（`java -version` 确认）
2. 下载 Community 版（免费）：https://neo4j.com/download-center/
3. Windows 解压后命令行启动：
   ```bash
   cd neo4j-community-5.xx/bin
   neo4j.bat console          # 前台启动，看到 "Started" 即成功
   ```
4. 浏览器打开 `http://localhost:7474`，首次登录改密码（默认 neo4j/neo4j）
5. Python 装驱动：`pip install neo4j`（官方驱动，py2neo 已停更，用官方）

### 1.3 三种跑 Cypher 的姿势

```bash
# 姿势 1：Neo4j Browser（浏览器输入框，最直观，推荐学习用）
http://localhost:7474

# 姿势 2：Python 官方驱动
python -c "
from neo4j import GraphDatabase
d = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', '你的密码'))
with d.session() as s:
    for r in s.run('MATCH (n) RETURN n LIMIT 5'):
        print(r)
"

# 姿势 3：cypher-shell 命令行
cd neo4j-community-5.xx/bin && cypher-shell -u neo4j -p 密码 "RETURN 1+1"
```

> 完整可运行的连库 demo 见 02_neo4j_python.py（安装 Neo4j 后执行）。

## 2. 术语速查

| 词汇 | 说明 |
|------|------|
| 属性图 | Property Graph：节点/关系都可带键值属性的图模型 |
| Cypher | Neo4j 查询语言，语法像 SQL 加上 ASCII 画图 (`(n)-[r]->(m)`) |
| Bolt | Neo4j 的二进制协议，Python 驱动默认走它（端口 7687） |
| 节点标签 | Label，给节点分类（类似表的表名）：`(:Person)` |
| 关系类型 | 边的类型名（类似三元组的关系）：`[:任职于]` |
