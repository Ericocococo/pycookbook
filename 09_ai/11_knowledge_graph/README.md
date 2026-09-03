# 知识图谱 —— Knowledge Graph

用结构化的图（节点 + 边）表示现实世界的实体及其关系，支撑语义搜索、智能问答、推荐等上层应用。

| 目录 | 内容 |
|------|------|
| [01_basics/](01_basics/) | 基础：概念、三元组、RDF vs 属性图、本体（OWL） |
| [02_graph_db/](02_graph_db/) | 图数据库：Neo4j、Cypher 查询语言、py2neo |
| [03_construction/](03_construction/) | 图谱构建：NER → 关系抽取 → 实体对齐 → 融合 |
| [04_reasoning/](04_reasoning/) | 推理：TransE、图神经网络（GNN）、规则推理、链接预测 |
| [05_application/](05_application/) | 应用：KBQA（知识问答）、GraphRAG、语义搜索 |

## 核心概念

| 术语 | 一句话 |
|------|--------|
| 三元组（Triple） | 知识图谱的最小单元：(头实体, 关系, 尾实体)，如 (北京, 首都of, 中国) |
| RDF | Resource Description Framework，W3C 标准的知识表示模型，语义网方向 |
| 属性图（Property Graph） | 节点和边都可带属性的图模型，Neo4j 等工业界图数据库的主流方案 |
| 本体（Ontology） | 领域知识的概念体系和约束规则，定义"有哪些类、类之间什么关系" |
| NER | Named Entity Recognition，命名实体识别，从文本中提取人名/地名/机构名等 |
| TransE | 知识表示学习经典模型，把实体和关系嵌入到向量空间：h + r ≈ t |
| KBQA | Knowledge Base Question Answering，把自然语言问题转成图谱查询 |
| GraphRAG | 用知识图谱增强大模型的检索增强生成（RAG） |

## 学习路线

```
基础概念 → 图数据库(Neo4j) → 图谱构建(抽取+融合) → 推理 → 应用(KBQA/GraphRAG)
   ①            ②                  ③                 ④          ⑤
```

快速上手路径：① → ② → ③（用 LLM 做抽取）→ ⑤（GraphRAG），跳过 ④ 推理部分，需要时再补。
