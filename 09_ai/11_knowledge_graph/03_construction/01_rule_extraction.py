"""规则抽取流水线 —— 从文本抽三元组（词典 NER + 触发词关系抽取）

Python 3.12 | 零依赖 | 运行：python 01_rule_extraction.py
演示：中文一句话文本 → 实体识别 → 关系判断 → 三元组 → 组装成图
术语：NER=Named Entity Recognition，命名实体识别，从文本找"人/公司/城市"类实体；
      RE=Relation Extraction，关系抽取，判断实体之间是什么关系；
      触发词=连接两个实体的动词（如"创立了"→ 创始人关系），是规则抽取的判断依据
"""

import re

import networkx as nx

# ============================================================
# ① 实体识别（NER）
# ============================================================

# 知识点 1.1：NER 任务 —— 找出"谁、哪个公司、哪个城市"
# 词典法 = 维护每个类型的词表，在文本里扫描匹配，最简单直接的 NER
# 适用场景：封闭领域（公司名录、产品名单）——词表可控，效果稳定
# 局限：新词出现就要人工加词（对比：机器学习 NER 能自动泛化）

PERSON = {"马云", "马化腾", "任正非"}          # 人物词典
COMPANY = {"阿里巴巴", "腾讯", "华为"}         # 公司词典
CITY = {"杭州", "深圳", "广州", "北京"}         # 城市词典

# 词表转成 (词→类型) 总表，一个字典统一管理三类
LEXICON = [(w, "人物") for w in PERSON] + \
          [(w, "公司") for w in COMPANY] + \
          [(w, "城市") for w in CITY]


def ner_scan(text: str):
    """词典扫描：返回实体列表 [(起始位置, 结束位置, 词, 类型)]"""
    entities = []
    for word, etype in LEXICON:
        # finditer 找词在文本里的每次出现（带位置）
        for m in re.finditer(re.escape(word), text):
            entities.append((m.start(), m.end(), word, etype))
    # 按位置排序：后面的"关系抽取"要看实体先后顺序
    entities.sort(key=lambda x: x[0])
    return entities


def demo01_ner():
    """① 实体识别"""
    print("① 词典 NER：扫描文本找出实体")

    # 文本里每个实体类型都要能抽出来（人物/公司/城市）
    text = ("马云创立了阿里巴巴，马化腾创办了腾讯，"
            "华为由任正非创立。阿里巴巴总部位于杭州，腾讯总部在深圳。")
    print(f"  原文: {text}")

    ents = ner_scan(text)
    for start, end, word, etype in ents:
        print(f"  [{start:2d}:{end:2d}] {word}  ← {etype}")
    return text, ents


# ============================================================
# ② 关系抽取（RE）
# ============================================================

# 知识点 2.1：关系抽取任务 —— 实体间是什么关系？
# 思路：实体已定位，就看"两个实体之间的文本"说了什么
# 触发词表：动词/短语 → 关系类型。例：之间出现"创立了" → 创始人关系
# 为什么能这么判？中文句式里动作词天然夹在两个论元之间

# 知识点 2.2：方向判断 —— 关系有方向，触发词位置定方向
# 正向句式：人物 创立了 公司        → (人物, 创始人, 公司)
# 反向句式：公司 由 人物 创立        → 仍是 (人物, 创始人, 公司)
# 所以看触发词的同时还要注意：人物在公司前=正向，公司在前=被动词倒装
# 教学简化：给"由...创立"类句式单独做反向处理，不做完整句法分析

TRIGGER_FOUNDER = r"创立|创办|创建|是.{0,4}创始人"   # 触发词：创始人关系
TRIGGER_HQ = r"总部位于|总部在"                     # 触发词：总部关系


def extract_relations(text: str, entities):
    """对相邻实体对做关系判断，返回三元组列表"""
    triples = []

    # 只检查"紧挨着"的实体对：前一个结束到后一个开始之间留短空隙
    # 空隙太长多半是两句话，不是同一件事（阈值 6 字）
    for i in range(len(entities) - 1):
        e1 = entities[i]
        e2 = entities[i + 1]
        gap = text[e1[1]:e2[0]]      # e1 结束 → e2 开始 的中间文本
        if len(gap) > 6:             # 间隔太长，跳过（跨句子）
            continue
        if re.search(r"[。！？；]", gap):  # 中间有断句标点 = 不是同一句，跳过
            continue

        # 从 e1 起点往后多看几字（覆盖"华为由任正非创立"触发词在 e2 之后的句式）
        window = text[e1[0]:min(e2[1] + 3, len(text))]

        # 场景 A：人物 → 公司（"马云 创立了 阿里巴巴"）
        if e1[3] == "人物" and e2[3] == "公司" and re.search(TRIGGER_FOUNDER, window):
            triples.append((e1[2], "创始人", e2[2]))
        # 场景 B：公司 → 人物（"华为 由 任正非 创立"——动作倒装，方向要换过来）
        elif (e1[3] == "公司" and e2[3] == "人物"
                and re.search(r"由" + r".{0,4}" + r"(创立|创办|创建)", window)):
            triples.append((e2[2], "创始人", e1[2]))
        # 场景 C：公司 → 城市（"阿里巴巴 总部位于 杭州"）
        elif e1[3] == "公司" and e2[3] == "城市" and re.search(TRIGGER_HQ, gap):
            triples.append((e1[2], "总部位于", e2[2]))

    # 去重（同一对实体可能被两个模式同时命中）
    return list(dict.fromkeys(triples))


def demo02_relation(text, entities):
    """② 关系抽取"""
    print("\n② 触发词关系抽取")
    triples = extract_relations(text, entities)
    for head, rel, tail in triples:
        print(f"  ({head}, {rel}, {tail})")
    return triples


# ============================================================
# ③ 组装流水线
# ============================================================

# 知识点 3.1：流水线 —— NER → RE → 建图，一键从文本到图谱
# 两个步骤的输出正好接上：NER 出实体，RE 出三元组，三元组直接喂图

# 知识点 3.2：规则法的局限 —— 为什么真实项目要换 LLM
# ① 漏抽：句子变个说法（"阿里1999年起步"）词典和触发词就抓瞎
# ② 误抽：词典撞名（"华为手机"里华为是产品线不是公司实体）
# ③ 词表维护成本：新公司/新句式都要人工补
# 大模型抽取 = 把文本 + 目标结构(schema) 丢给 LLM，让它直接返回 JSON
# 三元组，零规则、能泛化 —— 现代主流做法（演示见 05_application/GraphRAG.md）

def demo03_pipeline(text):
    """③ 完整流水线 + 规则法局限展示"""
    print("\n③ 流水线：文本 → 三元组 → 图谱")

    entities = ner_scan(text)
    triples = extract_relations(text, entities)

    g = nx.DiGraph()
    for head, rel, tail in triples:
        g.add_edge(head, tail, relation=rel)

    print(f"  实体 {g.number_of_nodes()} 个, 三元组 {g.number_of_edges()} 条")
    for head, tail in g.edges:
        print(f"    ({head}) --[{g[head][tail]['relation']}]--> ({tail})")

    # 局限演示：换个说法就漏抽 —— "张勇担任阿里巴巴CEO" 无触发词
    text2 = "张勇担任阿里巴巴CEO。"
    ents2 = ner_scan(text2)  # 注意：张勇不在词典里 → 实体都抽不到
    trips2 = extract_relations(text2, ents2)
    print(f"\n  局限演示: “{text2}”")
    print(f"    NER 结果: {[e[2] for e in ents2] or '空（张勇不在词典中）'}")
    print(f"    三元组: {trips2 or '空（无触发词命中）'}")
    print("    → 新实体靠词典、新句式靠模板，这就是规则法的天花板")


if __name__ == "__main__":
    text, ents = demo01_ner()
    demo02_relation(text, ents)
    demo03_pipeline(text)
