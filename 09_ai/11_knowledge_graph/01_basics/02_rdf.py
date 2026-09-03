"""RDF 标准模型 —— W3C 官方的知识表示语言

Python 3.12 | 依赖：rdflib | 运行：python 02_rdf.py
演示：用 rdflib 构建 RDF 图谱、模式查询、SPARQL 查询
术语：RDF=Resource Description Framework，资源描述框架；
      URI=统一资源标识符，给实体一个全局唯一"地址"；
      SPARQL=RDF 数据的查询语言（RDF 世界的 SQL）
"""

from rdflib import Graph, Literal, Namespace
from rdflib.namespace import RDF, RDFS

# ============================================================
# ① 构建 RDF 图谱
# ============================================================

# 知识点 1.1：RDF 是什么
# RDF 用"主语-谓语-宾语"三元组表达知识，和 01_triple.py 的三元组本质相同，
# 但多了两条硬规则：① 实体必须用 URI 全局唯一标识，杜绝两个"北京"搞混；
# ② 主语/谓语必须是 URI，宾语可以是实体(URI)或字面量(Literal 如字符串/数字)
# 由 W3C 标准化 → 语义网(Semantic Web)时代各家数据可以互联

# 知识点 1.2：命名空间 Namespace —— 给实体起"地址"
# 完整 URI 很长（http://example.org/kg/北京），用 Namespace 加前缀缩写
# KG = http://example.org/kg/ 的前缀；KG.北京 即完整 URI
# URL 只是标识符，不要求真实可访问——就像身份证号不要求能拨打电话

KG = Namespace("http://example.org/kg/")

# 知识点 1.3：add() 存三元组
# add((主语, 谓语, 宾语)) —— 三要素缺一不可
# 宾语两种形态：实体 → 用 KG.xxx（URI）；字面值 → 用 Literal("...")
# RDF.type 表示"属于某类"（北京 是 City 类），RDFS.label 给实体挂人类可读标签
# 这些都是 RDF 标准自带的谓语（谓语的"谓语"），类似 Python 的保留字

def demo01_build():
    """① 构建 RDF 图谱"""
    print("① 构建 RDF 图谱")

    g = Graph()  # rdflib 的图对象

    g.add((KG.北京, RDF.type, KG.City))                       # 北京 属于 City 类
    g.add((KG.北京, KG.首都Of, KG.中国))                       # 实体-实体：北京是中国的首都
    g.add((KG.阿里巴巴, KG.总部位于, KG.杭州))                  # 实体-实体：总部在杭州
    g.add((KG.杭州, RDFS.label, Literal("杭州", lang="zh")))   # 字面量：中文标签，带语言代码
    g.add((KG.杭州, KG.人口, Literal("1250", datatype=KG.万)))  # 字面量：带单位类型

    print(f"  三元组总数: {len(g)}")
    for s, p, o in g:  # 遍历打印；rdflib 自动把长 URI 缩写为 ns:名字 形式
        print(f"    ({s}, {p}, {o})")

    return g


# ============================================================
# ② 模式查询
# ============================================================

def demo02_query(g: Graph):
    """② 遍历查询"""

    # 知识点 2.1：triples((s, p, o)) 模式匹配
    # 给三元组的每个位置填值或 None：None = 任意匹配
    # 这就是"查询的本质"：固定部分填值，想找的留 None，返回所有命中项
    # 三种常见姿势：查宾语固定(首都)、查类型固定(所有城市)、查主语固定(杭州的属性)

    print("② 三元组查询")

    # 姿势 1：固定宾语 —— 谁是中国的首都？
    for s, p, o in g.triples((None, KG.首都Of, KG.中国)):
        print(f"  中国的首都: {s}")

    # 姿势 2：固定类型 —— 所有 City 类实体（类型也是谓语，可当普通关系查）
    for s, p, o in g.triples((None, RDF.type, KG.City)):
        print(f"  City 类型: {s}")

    # 姿势 3：固定主语 —— 杭州都有哪些属性？（谓语和宾语都留空）
    for s, p, o in g.triples((KG.杭州, None, None)):
        print(f"  杭州的属性: {p} → {o}")


# ============================================================
# ③ SPARQL 查询
# ============================================================

def demo03_sparql(g: Graph):
    """③ SPARQL 查询"""

    # 知识点 3.1：SPARQL 是什么
    # SPARQL = RDF 的官方查询语言，语法长得像 SQL 的 SELECT ... WHERE
    # 区别：SQL 查表(二维行)，SPARQL 查三元组模式(带 ? 前缀的变量任意匹配)
    # 掌握 triples() 后学 SPARQL 很顺——它就是 triples() 的"SQL 版写法"

    print("\n③ SPARQL 查询")

    # 知识点 3.2：SELECT 基础 —— ?变量 即 triples() 里的 None 位置
    # 每条三元组模式末尾要加" . "（句点）结束，对应 SQL 里的分号
    # PREFIX 可省，直接写完整 URI 用 <尖括号> 包起来
    # 例：问"谁创立了什么"，中文场景问"首都关系"

    # 查: 中国的首都（?capital 是我们要的答案变量）
    results = g.query("""
        SELECT ?capital WHERE {
            ?capital <http://example.org/kg/首都Of> <http://example.org/kg/中国> .
        }
    """)
    for row in results:
        print(f"  中国的首都: {row.capital}")

    # 知识点 3.3：多变量与"任一实体"
    # 同一查询里可多个 ?变量；两行三元组模式可表达"路径"
    # 例：谁的总部在杭州？(实体?) --总部位于--> 杭州

    results = g.query("""
        SELECT ?company WHERE {
            ?company <http://example.org/kg/总部位于> <http://example.org/kg/杭州> .
        }
    """)
    for row in results:
        print(f"  总部在杭州的公司: {row.company}")


if __name__ == "__main__":
    graph = demo01_build()
    demo02_query(graph)
    demo03_sparql(graph)
