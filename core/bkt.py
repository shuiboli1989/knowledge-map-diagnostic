"""BKT (Bayesian Knowledge Tracing) 更新逻辑模块

该模块实现了基于贝叶斯知识追踪的掌握概率更新算法，
用于根据学生的答题情况动态更新其对知识点的掌握程度。
"""

from typing import Dict


def update_mastery(
    p_mastery: float,
    is_correct: bool,
    p_slip: float = 0.15,
    p_guess: float = 0.25,
    p_transit: float = 0.1
) -> float:
    """根据答题结果更新掌握概率（标准四参数 BKT）

    标准 BKT 分两步：
    1. 贝叶斯后验更新：根据答题结果修正掌握概率
    2. 学习转移：练习本身带来的学习效果，未掌握→掌握

    Args:
        p_mastery: 当前掌握概率 P(Lₙ)
        is_correct: 答题结果（True=答对，False=答错）
        p_slip: 失误率 P(S)，已掌握但答错的概率，默认 0.15
        p_guess: 猜测率 P(G)，未掌握但答对的概率，默认 0.25
        p_transit: 学习转移概率 P(T)，每次练习从未掌握转为掌握的概率，默认 0.1

    Returns:
        float: 更新后的掌握概率（保留四位小数，限制在 [0.01, 1.0] 区间内）
    """
    p_correct_given_mastery = 1 - p_slip
    p_correct_given_not_mastery = p_guess

    # 步骤1：贝叶斯后验更新
    p_answer_correct = p_correct_given_mastery * p_mastery + p_correct_given_not_mastery * (1 - p_mastery)

    if is_correct:
        p_posterior = (p_correct_given_mastery * p_mastery) / p_answer_correct
    else:
        p_posterior = ((1 - p_correct_given_mastery) * p_mastery) / (1 - p_answer_correct)

    # 步骤2：学习转移 — 练习本身带来学习效果
    p_new = p_posterior + (1 - p_posterior) * p_transit

    # 下限防止概率归零，上限允许到 1.0
    p_new = max(0.01, min(1.0, p_new))
    return round(p_new, 4)


def update_student_state(
    student_data: dict,
    node_id: str,
    is_correct: bool
) -> dict:
    """更新学生的知识状态

    Args:
        student_data: 学生数据
        node_id: 知识点ID
        is_correct: 答题结果

    Returns:
        dict: 更新后的学生数据
    """
    if node_id in student_data['node_states']:
        node_state = student_data['node_states'][node_id]
        # 更新掌握概率
        node_state['p_mastery'] = update_mastery(node_state['p_mastery'], is_correct)
        # 增加答题次数
        node_state['answered_count'] += 1
        # 更新最后更新时间
        node_state['last_updated'] = "2026-03-23T00:00:00"  # 使用当前日期
    
    return student_data
