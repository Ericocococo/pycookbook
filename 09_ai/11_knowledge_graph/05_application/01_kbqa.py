"""KBQA 演示 —— 自然语言问句 → 图查询 → 答案

Python 3.12 | 零依赖 | 运行：python 01_kbqa.py
演示：给定小知识图谱，解析"总部在哪/谁创立的/创立了什么"三类问句并回答
术语：KBQA=Knowledge Base Question Answering，知识库问答；
      模板匹配=正则识别问句意图(在问"关系")，再结合词典找出实体

关联学习：图谱数据沿用 03_construction 的规则抽取结果（文本→三元组）
"""

import re

import networkx as nx

# ============================================================
# ① 准备：图谱 + 词典
# ============================================================

# 知识点 1.1：QA 的前提是"知识库里确实有答案"
# 下面三元组可以理解为 03_construction 规则抽取跑出来的结果入库：
# 文本 "马云创立了阿里巴巴…总部位于杭州" → 这些三元组
TRIPLES = [
    ("马云", "创始人", "阿里巴巴"),
    ("马化腾", "创始人", "腾讯"),
    ("任正非", "创始人", "华为"),
    ("阿里巴巴", "总部位于", "杭州"),
    ("腾讯", "总部位于", "深圳"),
    ("华为", "总部位于", "深圳"),
    ("杭州", "属于", "浙江"),
    ("深圳", "属于", "广东"),
    ("北京", "首都Of", "中国"),
]

# 实体词典：问句里识别"在问哪个实体"（词表可控场景，复用 03 的词典思路）
PERSON = {"马云", "马化腾", "任正非"}
COMPANY = {"阿里巴巴", "腾讯", "华为"}
CITY = {"杭州", "深圳", "广州", "北京"}
COUNTRY = {"中国"}


def demo01_build_graph():
    """① 建图"""
    print("① 知识图谱（来自文本抽取的 9 条三元组）")
    g = nx.DiGraph()
    for head, rel, tail in TRIPLES:
        g.add_edge(head, tail, relation=rel)
    for head, tail in g.edges:
        print(f"    ({head}) --[{g[head][tail]['relation']}]--> ({tail})")
    return g


# ============================================================
# ② 问句解析
# ============================================================

# 知识点 2.1：问句两步解析 —— 先认实体，再认意图
# 第一步 认实体：问句里出现哪个词典词 → 知道"在问谁"
#   "阿里巴巴的总部在哪" → 实体：阿里巴巴
# 第二步 认意图：问句文字匹配哪类模式 → 知道"想查什么关系"
#   "总部在哪" → 查 总部位于 关系
# 两步都成功才查图；识别失败 → 诚实说答不了（不要硬编答案）

# 知识点 2.2：意图模式表 —— 规则问答的"可答问题清单"
# 每类问题 = (意图名, 正则模式, 关系, 方向)
# 方向 forward：从实体出发顺查；backward：倒查谁连到该实体
# 关系为 None 的特殊意图（如"在哪里"）：不限关系，顺查全部
INTENTS = [
    # 问总部：{公司}的总部在哪 → 顺查 总部位于
    ("查总部", r"总部(位于|在|在哪|在哪里|在哪儿)", "总部位于", "forward"),
    # 问创始人：{公司}是谁创立的 → 倒查 创始人
    ("查创始人", r"(是|由).{0,3}(谁|谁们).{0,4}(创立|创办|创建)", "创始人", "backward"),
    ("查创始人", r"(谁|谁们).{0,3}(创立|创办|创建)了", "创始人", "backward"),
    # 问创业：{人物}创立了什么 → 顺查 创始人
    ("查创业", r"(创立|创办|创建)了(什么|哪些|啥)", "创始人", "forward"),
    # 问首都：谁是中国首都 / 中国的首都是谁 → 倒查 首都Of
    ("查首都", r"首都(是)?(谁|哪里|哪)", "首都Of", "backward"),
    # 问方位：{实体}在哪里（不限关系，顺查全部 → 北京→中国、杭州→浙江）
    ("查方位", r"在哪里?|在哪儿", None, "forward"),
]


def parse_question(q: str):
    """问句解析：返回 (实体, 实体类型, 意图) 或 None"""
    # 第一步：实体识别 —— 按长度降序匹配，防短词先命中（如"华为"在"华为手机"里）
    words = sorted(PERSON | COMPANY | CITY | COUNTRY, key=len, reverse=True)
    entity = None
    for w in words:
        if w in q:
            entity = w
            break
    if not entity:
        return None, None, None

    # 第二步：意图识别 —— 逐条试模式
    for _, pattern, rel, direction in INTENTS:
        if re.search(pattern, q):
            return entity, rel, direction
    return None, None, None  # 问法不在清单里 → 答不了


def demo02_parse():
    """② 展示解析过程"""
    print("\n② 问句解析（实体 + 意图两步）")
    for q in ["阿里巴巴的总部在哪里？", "华为是谁创立的？", "马化腾创立了什么？",
              "今天的天气怎么样？"]:
        entity, rel, direction = parse_question(q)
        if rel is None:
            print(f"  问: {q}\n    → 实体={entity}, 意图=未识别")
        else:
            print(f"  问: {q}\n    → 实体={entity}, 意图={rel}({direction})")


# ============================================================
# ③ 图查询 + 答案组装
# ============================================================

# 知识点 3.1：查图 —— 意图定了，查询就是 01_basics 学过的遍历
# forward：找 实体 --关系--> ?   顺着一跳（successors）
# backward：找 ? --关系--> 实体  倒着查（predecessors）
# 这步最简单：解析做好了，查询 = 已学的图遍历代码

# 知识点 3.2：答案组装 —— 顺带做"多跳增强"
# 答"阿里巴巴总部在哪"只查到杭州；连一步"杭州属于浙江"，
# 答成"杭州（浙江省）"——KBQA 的常见加分项（省/市/国家 联动）
# 多跳查询在 01_basics 知识点 2.3 出现过，这里直接复用思路

def answer_question(g: nx.DiGraph, q: str) -> str:
    """问答主函数：问句 → 答案字符串"""
    entity, rel, direction = parse_question(q)
    if not entity:
        return "  没听懂：我不认识这个问题里的实体/问法"

    # forward：顺查尾实体；backward：倒查头实体
    # rel 为 None（"在哪里"类）→ 不过滤关系，列出该方向全部连接
    if direction == "forward":
        results = [t for h, t in g.edges
                   if h == entity and (rel is None or g[h][t]["relation"] == rel)]
    else:
        results = [h for h, t in g.edges
                   if t == entity and (rel is None or g[h][t]["relation"] == rel)]

    if not results:
        if rel is None:
            return f"  抱歉，图谱里没有 {entity} 相关的连接信息"
        return f"  抱歉，图谱里没有 {entity} 的{rel}信息"

    # 多跳增强：城市答案顺带问一句"属于哪个省"
    text = "、".join(results)
    if rel == "总部位于":
        extra = []
        for city in results:
            for h, t in g.edges:
                if h == city and g[h][t]["relation"] == "属于":
                    extra.append(f"{city}（{t}）")
        text = "、".join(extra or results)
    return f"  {text}"


def demo03_qa(g: nx.DiGraph):
    """③ 问答演示"""
    print("\n③ 问答")
    for q in ["阿里巴巴的总部在哪里？", "华为是谁创立的？", "马化腾创立了什么？",
              "中国的首都是谁？", "北京在哪里？", "今天的天气怎么样？"]:
        print(f"  问: {q}")
        print(answer_question(g, q))


if __name__ == "__main__":
    graph = demo01_build_graph()
    demo02_parse()
    demo03_qa(graph)
