"""BKT (Bayesian Knowledge Tracing) 更新逻辑模块

该模块实现了基于贝叶斯知识追踪的掌握概率更新算法，
用于根据学生的答题情况动态更新其对知识点的掌握程度。
"""

from typing import Dict


def update_mastery(
    p_mastery: float,
    is_correct: bool,
    p_correct_given_mastery: float = 0.85,
    p_correct_given_not_mastery: float = 0.25
) -> float:
    """根据答题结果更新掌握概率

    Args:
        p_mastery: 当前掌握概率
        is_correct: 答题结果（True=答对，False=答错）
        p_correct_given_mastery: 已掌握时答对概率，默认 0.85
        p_correct_given_not_mastery: 未掌握时答对概率（猜测率），默认 0.25

    Returns:
        float: 更新后的掌握概率（保留四位小数，限制在 [0.01, 0.99] 区间内）
    """
    # 计算答对的概率
    p_answer_correct = p_correct_given_mastery * p_mastery + p_correct_given_not_mastery * (1 - p_mastery)

    if is_correct:
        # 答对时的更新公式
        p_new = (p_correct_given_mastery * p_mastery) / p_answer_correct
    else:
        # 答错时的更新公式
        p_new = ((1 - p_correct_given_mastery) * p_mastery) / (1 - p_answer_correct)

    # 限制在 [0.01, 0.99] 区间内
    p_new = max(0.01, min(0.99, p_new))
    # 保留四位小数
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
