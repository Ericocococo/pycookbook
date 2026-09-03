"""TransE —— 用向量算术做知识推理

Python 3.12 | 依赖：numpy | 运行：python 01_transe.py
演示：纯 numpy 实现 TransE，训练后用向量推理补全缺失的三元组
术语：TransE=Translating Embedding，平移嵌入模型，核心假设 h + r ≈ t；
      Embedding=嵌入，把符号(实体/关系)映射成稠密向量的过程；
      Margin Loss=边际损失，让正负样本分数拉开一个边距的损失函数
"""

import numpy as np

# ============================================================
# ① 数据准备
# ============================================================

# 知识点 1.1：图谱不完整 —— 推理要解决的问题
# 图谱里只有"杭州属于浙江、浙江属于中国"，没写"北京属于中国"。
# 但图谱有 (北京,首都Of,中国) —— 模型要能学到规律：
# "跟中国有 首都Of 关系的地方，也属于中国"，从而补全缺失知识
# 推理模型的目标 = 自动学到这类潜在规律，补全缺失知识

# 实体：所有可能成为节点的事物（人 / 公司 / 城市 / 省 / 国家 五类）
ENTITIES = ["马云", "张勇", "井贤栋", "马化腾", "刘炽平", "任正非", "梁华",
            "阿里巴巴", "蚂蚁集团", "腾讯", "华为",
            "杭州", "深圳", "广州", "宁波", "浙江", "广东", "北京", "中国"]
# 关系：所有可能的边类型
RELATIONS = ["创始人", "CEO", "总部位于", "属于", "首都Of"]

# 已有三元组（正样本）：图谱里被确认的事实
# 刻意设计：每类关系多条样本，模型才学得出"规律"而不是背答案
TRIPLES = [
    # 人 → 公司（创始人 / CEO）
    ("马云", "创始人", "阿里巴巴"),
    ("马云", "创始人", "蚂蚁集团"),
    ("马化腾", "创始人", "腾讯"),
    ("任正非", "创始人", "华为"),
    ("张勇", "CEO", "阿里巴巴"),
    ("井贤栋", "CEO", "蚂蚁集团"),
    ("刘炽平", "CEO", "腾讯"),
    ("梁华", "CEO", "华为"),
    # 公司 → 城市（总部位于）
    ("阿里巴巴", "总部位于", "杭州"),
    ("蚂蚁集团", "总部位于", "杭州"),
    ("腾讯", "总部位于", "深圳"),
    ("华为", "总部位于", "深圳"),
    # 城市 → 省（属于）
    ("杭州", "属于", "浙江"),
    ("宁波", "属于", "浙江"),
    ("深圳", "属于", "广东"),
    ("广州", "属于", "广东"),
    # 省 → 国家（属于）
    ("浙江", "属于", "中国"),
    ("广东", "属于", "中国"),
    # 首都
    ("北京", "首都Of", "中国"),
    # ★缺失的知识（训练集里没有，留给推理环节预测）：
    #   (北京, 属于, 中国)   —— 靠"首都Of 连着中国"推断
    #   (杭州, 总部位于, ?)  —— 该问杭州 总部在杭州的公司？（反方向预测见③）
]


def demo01_prepare():
    """① 准备数据"""
    print("① 数据：%d 实体、%d 关系、%d 条已知三元组"
          % (len(ENTITIES), len(RELATIONS), len(TRIPLES)))
    # 建立 名称→序号 索引：向量矩阵按行号存取，名字只是"查字典"的钥匙
    return ({n: i for i, n in enumerate(ENTITIES)},
            {n: i for i, n in enumerate(RELATIONS)})


# ============================================================
# ② 训练
# ============================================================

# 知识点 2.1：向量化 —— 实体/关系都变成 d 维向量
# 实体向量表 e[i]：第 i 行 = 第 i 个实体的向量，可理解为该实体的"语义指纹"
# 关系向量表 r[j]：第 j 行 = 第 j 个关系的向量，可理解为"平移方向"
# 初始值随机给（高斯噪声×0.1 保持小幅度），训练中逐渐学出语义

# 知识点 2.2：TransE 核心假设与评分函数
# 假设：头向量 + 关系向量 ≈ 尾向量    (h + r ≈ t)
# 评分函数 d(h, r, t) = ‖h + r - t‖₁  —— L1 距离，衡量"不满足程度"
# 分数越小 = 三元组越可能是真的；理想状态：正样本分数→0，负样本分数→大
# L1 距离（绝对值之和）比 L2 对异常值更鲁棒，是 TransE 论文的常用选择

def demo02_train(e_idx, r_idx, epochs=800, dim=16, lr=0.02, margin=1.0):
    """② 训练：SGD + 负采样 + margin loss"""
    print("\n② 训练 TransE（dim=%d, epochs=%d）" % (dim, epochs))

    rng = np.random.default_rng(0)
    # 向量矩阵：实体 n×d、关系 m×d；随机初始化后做 L2 归一化(向量长度=1)
    # 归一化防向量长度随意膨胀——长度只跟"语义距离"有关才能比较
    entity_vec = rng.normal(0, 0.1, (len(ENTITIES), dim))
    rel_vec = rng.normal(0, 0.1, (len(RELATIONS), dim))
    entity_vec /= np.linalg.norm(entity_vec, axis=1, keepdims=True)

    # 三元组转成索引三元组 (i, j, k)，训练循环里只碰数字不碰字符串
    triples = [(e_idx[h], r_idx[r], e_idx[t]) for h, r, t in TRIPLES]

    # 知识点 2.3：负采样 —— 正样本的"假兄弟"
    # 每个正样本造一个负样本：随机替换头或尾为别的实体
    # 例：正(马云,创始人,阿里巴巴) → 负(张勇,创始人,阿里巴巴)（张勇没创立阿里）
    # 为什么必须造假的？模型没见过"什么是不对"就学不会"什么是对"
    def negative(h, r, t):
        while True:  # 重采样直到换成真负样本（避免恰好替换出正样本）
            if rng.random() < 0.5:
                nh = rng.integers(0, len(ENTITIES))
                if (nh, r, t) not in triples:
                    return (nh, r, t)
            else:
                nt = rng.integers(0, len(ENTITIES))
                if (h, r, nt) not in triples:
                    return (h, r, nt)

    # 知识点 2.4：训练循环 —— margin loss + 随机梯度下降
    # loss = max(0, margin + d(正样本) - d(负样本))
    # 直觉：正样本分(距离)必须比负样本低至少 margin，否则计损失
    # 梯度用数值近似即可——演示代码不手推导数公式，np 对向量求导晦涩，
    # 采用"解析式一步到位"：d = sum|h+r-t|，其梯度符号由差值决定
    for epoch in range(epochs):
        total_loss = 0.0
        for h, r, t in triples:
            nh, _, nt = negative(h, r, t)  # 造负样本

            # 前向：算正负样本距离（分数）
            diff_pos = entity_vec[h] + rel_vec[r] - entity_vec[t]
            diff_neg = entity_vec[nh] + rel_vec[r] - entity_vec[nt]

            # L1 距离对每个分量的梯度 = sign(分量)（绝对值函数导数 = 符号）
            # 反向更新：loss 变大 = 正距离↑负距离↓；要降 loss 就反向移动
            d_pos = np.abs(diff_pos).sum()
            d_neg = np.abs(diff_neg).sum()
            if margin + d_pos - d_neg > 0:  # 未满足"拉开 margin"才有损失
                # 推正样本更近：向量沿 -sign(diff) 方向移动（公式推导结果）
                entity_vec[h] -= lr * np.sign(diff_pos)
                rel_vec[r] -= lr * np.sign(diff_pos)
                entity_vec[t] += lr * np.sign(diff_pos)
                # 推负样本更远：反向操作（h 越远离 t 组合，r 反向往回拉）
                entity_vec[nh] += lr * np.sign(diff_neg)
                rel_vec[r] -= lr * np.sign(diff_neg)
                entity_vec[nt] -= lr * np.sign(diff_neg)
                total_loss += margin + d_pos - d_neg

        # 每轮结束重新归一化实体向量（约束长度，训练稳定的关键）
        entity_vec /= np.linalg.norm(entity_vec, axis=1, keepdims=True)

        if epoch % 100 == 0 or epoch == epochs - 1:
            print(f"  epoch {epoch:4d}  loss={total_loss:.4f}")

    return entity_vec, rel_vec


# ============================================================
# ③ 推理：用学到的向量补全知识
# ============================================================

# 知识点 3.1：链接预测 —— 向量推理的落地方式
# 问"X 的 CEO 是谁？"→ 取 head=X 的向量，加关系 CEO 的向量，
# 遍历所有实体找 h + r 最接近谁（距离最小），最近的那个就是答案
# 把 h + r 当作"理想答案向量"，和所有候选实体向量比距离 → 排序出答案
# 补头方向同理：t - r 当作"理想头向量"（详见下面的 predict_rev）

# 知识点 3.2：逆向预测 —— 补头与补尾对称
# 正问 h + r ≈ t，反用 t - r ≈ h，同一套向量两种问法都能答

def predict_rev(tail, rel, id2ent, entity_vec, rel_vec, e_idx, r_idx, topk=3):
    """逆向预测头实体：t - r 理想向量找最近实体"""
    target = entity_vec[e_idx[tail]] - rel_vec[r_idx[rel]]
    dists = np.linalg.norm(entity_vec - target, axis=1)
    order = np.argsort(dists)
    return [(id2ent[i], round(float(dists[i]), 3)) for i in order][:topk]


def demo03_predict(entity_vec, rel_vec, e_idx, r_idx):
    """③ 推理：链接预测"""
    print("\n③ 链接预测（图谱里没写，用向量推出来）")

    id2ent = {i: n for n, i in e_idx.items()}

    def predict(head, rel, topk=3, exclude=()):
        """给定头实体+关系，预测最可能的尾实体"""
        # h + r 理想向量 vs 全部实体向量，L2 距离（这里用 L2 更平滑易排序）
        target = entity_vec[e_idx[head]] + rel_vec[r_idx[rel]]
        dists = np.linalg.norm(entity_vec - target, axis=1)
        # 按距离升序取前 topk 个
        # exclude 排除已知答案和头实体自身（h+r 离自己最近是退化答案，没意义）
        order = np.argsort(dists)
        return [(id2ent[i], round(float(dists[i]), 3)) for i in order
                if id2ent[i] not in {head} | set(exclude)][:topk]

    # 案例 1：补全缺失知识 —— (北京, 属于, ?)
    # 训练集从没出现过这个三元组，全靠"北京首都Of中国"和"各省属于中国"推断
    print("  (北京, 属于, ?)       → 候选:", predict("北京", "属于"))

    # 案例 2：总部推理 —— 华为 总部位于 ?（深圳在训练集里出现过，验证记忆）
    print("  (华为, 总部位于, ?)   → 候选:", predict("华为", "总部位于"))

    # 案例 3：组合推理 —— 马云 创始人 蚂蚁集团已知，问 马云 创始人 还创建过谁？
    # 训练里马云只有两条创始人边；模型应推"还创建了和阿里同省的公司"（较难，看结果）
    print("  (马云, 创始人, ?)     → 候选:",
          predict("马云", "创始人", exclude={"阿里巴巴", "蚂蚁集团"}))

    # 案例 4：逆向补头 —— 谁是 中国的首都？t - r 反推 h
    print("  (?, 首都Of, 中国)     → 候选:",
          predict_rev("中国", "首都Of", id2ent, entity_vec, rel_vec, e_idx, r_idx))


if __name__ == "__main__":
    e_idx, r_idx = demo01_prepare()
    e_vec, r_vec = demo02_train(e_idx, r_idx)
    demo03_predict(e_vec, r_vec, e_idx, r_idx)
