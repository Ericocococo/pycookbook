# 05_application 应用 —— 让图谱被用起来

> 图谱建好存好了，怎么让用户问出答案？两大经典应用：
> **KBQA**（知识问答：自然语言 → 图查询）和 **GraphRAG**（给大模型当外部知识）。

| 文件 | 内容 |
|------|------|
| [01_kbqa.py](01_kbqa.py) | KBQA 演示：模板匹配问题解析 + 图查询，可运行零依赖 |
| [02_graphrag.md](02_graphrag.md) | GraphRAG：知识图谱 + 大模型检索增强（概念 + 架构） |

## 1. 知识点

### 1.1 KBQA 的两种路线

| 路线 | 做法 | 特点 |
|------|------|------|
| 模板规则（本目录） | 正则匹配问句模式 → 查图 | 可控可跑，但只能答"写过的问法" |
| 语义解析 / LLM | 问句 → 意图理解 → 生成 Cypher | 能泛化问法，工程量大，见 02_graphrag.md |

### 1.2 GraphRAG 与普通 RAG 的区别

| | 普通 RAG（向量检索） | GraphRAG（图谱检索） |
|---|---|---|
| 索引 | 文本切片 → 向量 | 文本 → 三元组 → 图 |
| 检索 | 向量相似度找段落 | 按实体找子图（一跳/多跳） |
| 强项 | 单点事实问答 | 多跳推理（"X 的供应商的供应商…"） |
| 代表作 | 通用标配 | 微软 GraphRAG（2024） |

## 2. 运行

```bash
python 01_kbqa.py            # KBQA 演示（零依赖）
pip install networkx         # 如未装
```

## 3. 术语速查

| 词汇 | 全称/英文 | 说明 |
|------|------|------|
| KBQA | Knowledge Base Question Answering | 知识库问答：自然语言问题 → 图查询 → 答案 |
| QA | Question Answering | 问答任务 |
| RAG | Retrieval-Augmented Generation | 检索增强生成：先检索外部知识再喂大模型 |
| GraphRAG | 图谱版 RAG | 检索对象从文本段落换成知识图谱子图 |
| 多跳 | Multi-hop | 需要沿关系走多步才能回答的问题 |
