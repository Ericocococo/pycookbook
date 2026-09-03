# 01_basics 基础概念 —— 三元组、RDF

> 知识图谱的第一课：搞懂"图"里存什么、怎么表示。
> README 的 `#### 1.1.X / 2.X.Y` 与对应 .py 里 `# 知识点 X.Y：` 注释一一对应。

## 1. 知识点 —— 01_triple.py（三元组 + networkx）

### 1.1 ① 构建图谱（对应 demo01，知识点 1.1 ~ 1.2）

#### 1.1.1 三元组是什么（对应 01_triple.py 知识点 1.1）

一句"事实" = 一个三元组：(头实体, 关系, 尾实体)。

- **实体**（Entity）= 人/公司/城市等对象 → 图谱的**节点**
- **关系**（Relation）= 实体间的语义联系 → 图谱的**边**

任何知识都能用主-谓-宾结构表达，机器才方便存和查：

```python
("马云", "阿里巴巴", "创始人")   # 马云是阿里巴巴的创始人
```

#### 1.1.2 用有向图存储三元组（对应 01_triple.py 知识点 1.2）

`networkx.DiGraph` 每条边带方向，正好表达关系方向性（"创始人"从马云指向阿里巴巴）。

```python
import networkx as nx

g = nx.DiGraph()                                # DiGraph = Directed Graph，有向图
g.add_edge("马云", "阿里巴巴", relation="创始人")  # relation= 把关系名挂到边的属性上
g.add_edge("阿里巴巴", "杭州", relation="总部位于")

# 边上的关系名：g[起点][终点] 返回边属性字典
print(g["马云"]["阿里巴巴"]["relation"])         # 创始人
```

### 1.2 ② 查询图谱（对应 demo02，知识点 2.1 ~ 2.4）

#### 1.2.1 正向查询 successors（对应 01_triple.py 知识点 2.1）

问"从某实体出发能到哪"——`successors` 返回该节点所有边的**出节点**。

```python
list(g.successors("马云"))     # ['阿里巴巴', '蚂蚁集团']
```

#### 1.2.2 按关系过滤（对应 01_triple.py 知识点 2.2）

查询本质 = 固定部分填值、想找的留空，遍历边过滤：

```python
[h for h, t in g.edges if t == "阿里巴巴" and g[h][t]["relation"] == "创始人"]
# → ['马云']  谁创立了阿里巴巴
```

#### 1.2.3 多跳路径（对应 01_triple.py 知识点 2.3）

单步答"总部在哪"，多跳答"总部在哪个省"。**路径查询是知识图谱相对关系数据库的核心优势**——数据库里要多表 JOIN 写长 SQL，图里顺着边走就行。

```python
for h, t in g.edges:
    if h == "阿里巴巴" and g[h][t]["relation"] == "总部位于":
        print(t)   # 第一跳：杭州
```

#### 1.2.4 反向查询 predecessors（对应 01_triple.py 知识点 2.4）

问"谁指向了某实体"——`predecessors` 返回所有边的**入节点**。

```python
list(g.predecessors("阿里巴巴"))   # ['马云', '张勇']
```

### 1.3 ③ 节点属性（对应 demo03，知识点 3.1）

#### 1.3.1 属性 vs 三元组（对应 01_triple.py 知识点 3.1）

- **关系** = 实体-实体 的连接 → 存成**边**
- **属性** = 实体-值 的描述（成立时间/人口）→ 存成节点上的**键值对**

```python
g.nodes["阿里巴巴"]["成立时间"] = "1999年"
g.nodes["杭州"]["人口"] = 1250
```

## 2. 知识点 —— 02_rdf.py（RDF + rdflib）

### 2.1 ① 构建 RDF 图谱（对应 demo01，知识点 1.1 ~ 1.3）

#### 2.1.1 RDF 是什么（对应 02_rdf.py 知识点 1.1）

RDF 与朴素三元组的差别在两条硬规则：

1. 实体必须用 **URI** 全局唯一标识，杜绝两个"北京"搞混
2. 主语/谓语必须是 URI；宾语可以是实体（URI）或字面量（Literal 字符串/数字）

由 W3C 标准化 → 语义网时代各家数据可互联。

#### 2.1.2 Namespace 命名空间（对应 02_rdf.py 知识点 1.2）

完整 URI 很长，用 Namespace 加前缀缩写。URL 只是**标识符**，不要求真实可访问（像身份证号不要求能拨打电话）。

```python
from rdflib import Namespace

KG = Namespace("http://example.org/kg/")
KG.北京    # 即完整 URI：http://example.org/kg/北京
```

#### 2.1.3 add() 存三元组（对应 02_rdf.py 知识点 1.3）

`add((主语, 谓语, 宾语))` 三要素缺一不可。宾语两形态：实体用 `KG.xxx`，字面值用 `Literal(...)`。`RDF.type` 表示"属于某类"，`RDFS.label` 挂人类可读标签。

```python
from rdflib import Graph, Literal
from rdflib.namespace import RDF, RDFS

g = Graph()
g.add((KG.北京, RDF.type, KG.City))                        # 北京 属于 City 类
g.add((KG.北京, KG.首都Of, KG.中国))                        # 实体-实体
g.add((KG.杭州, RDFS.label, Literal("杭州", lang="zh")))    # 字面量，带语言标签
```

### 2.2 ② 模式查询（对应 demo02，知识点 2.1）

#### 2.2.1 triples() 模式匹配（对应 02_rdf.py 知识点 2.1）

`triples((主语, 谓语, 宾语))` 每个位置填值或 `None`，None = 任意匹配：

```python
g.triples((None, KG.首都Of, KG.中国))    # 姿势1：固定宾语 → 谁是中国首都
g.triples((None, RDF.type, KG.City))     # 姿势2：固定类型 → 所有 City（类型也是谓语）
g.triples((KG.杭州, None, None))          # 姿势3：固定主语 → 杭州的属性
```

### 2.3 ③ SPARQL 查询（对应 demo03，知识点 3.1 ~ 3.3）

#### 2.3.1 SPARQL 是什么（对应 02_rdf.py 知识点 3.1）

SPARQL = RDF 官方查询语言，语法像 SQL 的 `SELECT ... WHERE`；区别是查**三元组模式**，`?变量` 即 triples() 里 None 的位置。

#### 2.3.2 SELECT 基础（对应 02_rdf.py 知识点 3.2）

每条三元组模式末尾要加 ` . `（句点）结束；可用完整 URI 免去 PREFIX 声明：

```python
results = g.query("""
    SELECT ?capital WHERE {
        ?capital <http://example.org/kg/首都Of> <http://example.org/kg/中国> .
    }
""")
for row in results:
    print(row.capital)
```

## 3. 运行

```bash
pip install networkx rdflib

python 01_triple.py   # 三元组构建 + 查询
python 02_rdf.py      # RDF + SPARQL
```

## 4. 术语速查

| 词汇 | 全称 | 说明 |
|------|------|------|
| 三元组 | Triple | 知识最小单元 (头实体, 关系, 尾实体) |
| RDF | Resource Description Framework | W3C 标准知识表示模型：三元组 + URI |
| URI | Uniform Resource Identifier | 统一资源标识符，实体全局唯一"地址" |
| SPARQL | SPARQL Protocol and RDF Query Language | RDF 的查询语言，语法类似 SQL |
| Literal | 字面量 | RDF 中的具体值（字符串/数字），不是实体 |
| DiGraph | Directed Graph | 有向图，networkx 中边带方向的图 |
| Namespace | 命名空间 | URI 前缀缩写，避免写完整长 URL |
