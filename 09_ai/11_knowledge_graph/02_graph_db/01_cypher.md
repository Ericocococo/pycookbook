# Cypher 语法速查 —— 用"画图"的方式写查询

> 对应 02_graph_db/README.md §1.3。Cypher 的杀手锏：查询模式长得就像画在纸上的图。
> 节点用括号 `(n)`，关系用方括号箭头 `-[r]->`，二者连起来就是一条"图谱图案"。

所有命令都可直接粘贴到 Neo4j Browser（http://localhost:7474）执行。

## 1. 建数据

### 1.1 建节点

```cypher
// CREATE 建节点；:Person 是节点标签（label），{...} 是属性
// 标签 = 给节点分类（类似表的表名），属性 = 键值对（类似表的行内容）
CREATE (p:Person {name: '马云'})
CREATE (c:Company {name: '阿里巴巴', founded: 1999})
```

对比 01_triple.py 的 networkx：属性直接写在创建语句里，不用事后补。

### 1.2 建关系

```cypher
// MATCH 先找到两个节点，CREATE 建它们之间的边
// [r:创始人]：r 是变量名，创始人 是关系类型（对应三元组的"关系"）
// 关系也能带属性 —— 属性图与纯三元组的差别之一
MATCH (a:Person {name: '马云'}), (b:Company {name: '阿里巴巴'})
CREATE (a)-[r:创始人 {since: 1999}]->(b)
```

## 2. 查询

### 2.1 全查 + 条件过滤

```cypher
// 查所有 Person
MATCH (p:Person) RETURN p

// WHERE 过滤：标签限类型，属性限取值
MATCH (p:Person) WHERE p.name = '马云' RETURN p
// 等价的简写（属性和标签直接内联在括号里，短查询更常用）
MATCH (p:Person {name: '马云'}) RETURN p
```

### 2.2 关系查询 —— 模式的威力

```cypher
// 谁创立了阿里巴巴：模式 = (谁)-[创始人]->(阿里巴巴)
// 箭头方向 = 关系的方向；不想管方向可写 -[]-（无箭头）
MATCH (p:Person)-[:创始人]->(c:Company {name: '阿里巴巴'}) RETURN p.name

// 反向：阿里巴巴和谁有关系（不限方向）
MATCH (c:Company {name: '阿里巴巴'})-[r]-(x) RETURN type(r), x.name
```

### 2.3 路径 / 多跳查询

```cypher
// 阿里巴巴总部在杭州，杭州在浙江 → 两跳路径
// [*1..3] = 沿任意关系走 1~3 跳（图的"深度遍历"，长度上限可控防爆炸）
MATCH (c:Company {name: '阿里巴巴'})-[:总部位于]->(:City)-[:省会]->(p:Province)
RETURN p.name

// 度查询：跟阿里巴巴直接相连的节点数与实体（图分析基础）
MATCH (c:Company {name: '阿里巴巴'})-[r]-(x) RETURN count(r) AS 连接数
```

## 3. 修改与删除

```cypher
// 更新属性（SET = 改字段）
MATCH (p:Person {name: '马云'}) SET p.title = '退休' RETURN p

// 删除：先删关系再删节点（DELETE 节点时若有边连着会报错）
MATCH (p:Person {name: '张勇'})-[r]-() DELETE r, p

// 清库（开发期常用，MATCH (n) 全图删除）
MATCH (n) DETACH DELETE n
```

## 4. 术语速查

| Cypher 关键字 | 说明 |
|------|------|
| MATCH | 查（找匹配模式的子图） |
| CREATE | 建节点/关系 |
| RETURN | 返回结果（类似 SELECT 的投影列） |
| WHERE | 过滤（类似 SQL 的 WHERE） |
| SET / DELETE | 改属性 / 删节点 |

| 图案符号 | 含义 |
|------|------|
| `(n)` | 节点，n = 变量名 |
| `(:Person)` | 标签为 Person 的节点 |
| `(n {name:'马云'})` | 带属性条件的节点 |
| `-[r:创始人]->` | 类型为创始人的**有向**关系 |
| `-[r]-` | 任意方向的关系 |
| `[*1..3]` | 1~3 跳的任意路径（图遍历） |
