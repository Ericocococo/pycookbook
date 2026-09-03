# GraphRAG —— 知识图谱 × 大模型

> 普通 RAG 检索**文本段落**，GraphRAG 检索**图谱子图**。
> 核心升级：能答需要多跳推理的问题（"A 公司老板的公司和 B 有关系吗"）。

## 1. 为什么需要 GraphRAG

### 1.1 普通 RAG 的短板

普通 RAG：文档切片 → 向量化 → 检索 Top-K 段落 → 拼 prompt 喂 LLM。

两个硬伤：

1. **多跳问题答不了**：问"华为的创始人的公司的总部在哪个省"，要先后用到 华为→任正非→(任正非的公司)→总部→省 的知识，这些事实分散在不同段落，向量检索按"相似度"找段落，单段里没有完整答案就抓瞎
2. **全局问题答不了**："这批文档里所有公司都在哪些城市"——需要跨段落汇总，Top-K 切片天然只覆盖局部

### 1.2 GraphRAG 的思路

文档先由 LLM 抽成**三元组**（就是本目录 03_construction 学的事，不过抽取者从规则换成 LLM）：

```
输入文本 → LLM 抽取 → (实体, 关系, 实体) 三元组 → 存图
问题进来 → 从问题抽实体 → 沿图取子图（1~3 跳） → 子图+问题 → LLM 总结答案
```

- 多跳问题 = 沿边多走几步（01_basics 知识点 2.3 的多跳查询）
- 全局问题 = 对图做社区划分（community detection），把稠密子图先各自总结，再汇总——微软 GraphRAG 论文的核心 trick

## 2. 架构对比

```
普通 RAG:             GraphRAG:
  文档                    文档
   │                      │ LLM 抽取三元组
   ▼                      ▼
  向量库 ──相似度检索──►  知识图谱 ──实体定位+子图扩展──►
   │                      │
   ▼                      ▼
 Top-K 段落            子图(节点+边+属性)
   │                      │
   ▼                      ▼
   LLM 回答              LLM 总结回答（答案可溯源到子图）
```

## 3. 什么时候用 GraphRAG

| 场景 | 选择 |
|------|------|
| 事实问答（"合同里违约金比例是多少"） | 普通 RAG 够用，简单 |
| 多跳推理（"X 的客户里谁还和 Y 有合作"） | GraphRAG 显著更强 |
| 文档总量大、关系密 | GraphRAG（建图成本高，值得） |
| 小文档、低频更新 | 普通 RAG（GraphRAG 建图要 LLM 抽一轮，费 token） |

## 4. 技术栈选型（学到这里要动手时的参考）

| 环节 | 可选 |
|------|------|
| LLM 抽取 | Claude API / GPT / 本地 Qwen（prompt: 给 schema 返回 JSON 三元组，思路见 [03_construction/README.md](../03_construction/README.md)） |
| 图谱存储 | Neo4j（见 [02_graph_db/](../02_graph_db/)） |
| 检索实现 | 先模板（[01_kbqa.py](01_kbqa.py)）后向量+图混合 |
| 框架 | 微软 GraphRAG（开源，pip install graphrag）/ LlamaIndex PropertyGraphIndex |

## 5. 动手路线（建议 Demo 化）

1. 拿 20 篇新闻/财报当语料
2. Claude 抽取三元组 → JSON → Neo4j
3. 问题先抽实体 → Cypher 取子图（02_graph_db 的 Cypher 语法）
4. 子图文本化 → 拼 prompt → Claude 总结
5. 对比普通 RAG 与 GraphRAG 在多跳问题上的答案质量

> 依赖 LLM API，放文档不放代码。跑通后欢迎回填为可运行配方。
