"""CAT (Computerized Adaptive Testing) 选题逻辑模块

该模块实现了自适应测试的选题算法，
根据学生的当前知识状态，选择最适合的题目进行测试，
以最大化信息增益。
"""

import random
from typing import Dict, List, Optional


def calculate_info_gain(p_mastery: float) -> float:
    """计算信息增益

    信息增益最大的情况是掌握概率接近 0.5 时

    Args:
        p_mastery: 掌握概率

    Returns:
        float: 信息增益值，越接近 0.5 信息增益越大
    """
    return abs(0.5 - p_mastery)


def count_untested_successors(graph_data: dict, node_id: str, student_data: dict) -> int:
    """计算节点的未测试后继节点数量

    Args:
        graph_data: 知识图谱数据
        node_id: 节点ID
        student_data: 学生数据

    Returns:
        int: 未测试后继节点数量
    """
    count = 0
    for node in graph_data.get('nodes', []):
        prerequisites = node.get('prerequisites', [])
        if node_id in prerequisites:
            successor_id = node.get('id')
            if successor_id in student_data.get('node_states', {}):
                answered_count = student_data['node_states'][successor_id].get('answered_count', 0)
                if answered_count < 3:
                    count += 1
    return count


def select_next_node(
    graph_data: dict,
    student_data: dict,
    questions: list[dict]
) -> Optional[str]:
    """选择下一个要测试的节点

    Args:
        graph_data: 知识图谱数据
        student_data: 学生数据
        questions: 题库

    Returns:
        str | None: 选中的节点ID，无可选节点时返回 None
    """
    # 1. 过滤掉已答题数 >= 3 的节点
    eligible_nodes = []
    node_states = student_data.get('node_states', {})
    
    for node in graph_data.get('nodes', []):
        node_id = node.get('id')
        if node_id in node_states:
            answered_count = node_states[node_id].get('answered_count', 0)
            if answered_count < 3:
                p_mastery = node_states[node_id].get('p_mastery', 0.5)
                info_gain = calculate_info_gain(p_mastery)
                untested_successors = count_untested_successors(graph_data, node_id, student_data)
                eligible_nodes.append((info_gain, -untested_successors, node_id))  # 负号用于排序

    if not eligible_nodes:
        return None

    # 2. 优先选择掌握概率最接近 0.5 的节点（info_gain 最小）
    # 3. 如果存在多个掌握概率相近（差值 < 0.05）的候选节点，
    #    优先选择拥有最多"未测试后继节点"的节点（-untested_successors 最小）
    eligible_nodes.sort()
    
    # 检查是否有多个掌握概率相近的候选节点
    best_info_gain = eligible_nodes[0][0]
    best_candidates = []
    
    for node in eligible_nodes:
        if abs(node[0] - best_info_gain) < 0.05:
            best_candidates.append(node)
        else:
            break
    
    if len(best_candidates) > 1:
        # 按未测试后继节点数量排序
        best_candidates.sort()
    
    return best_candidates[0][2]


def select_next_question(
    node_id: str,
    student_data: dict,
    questions: list[dict]
) -> Optional[dict]:
    """从选中节点的题库中选择一道学生未做过的题目

    Args:
        node_id: 节点ID
        student_data: 学生数据
        questions: 题库

    Returns:
        dict | None: 选中的题目字典，无可用题时返回 None
    """
    # 获取该节点的所有题目
    node_questions = [q for q in questions if q.get('node_id') == node_id]
    
    if not node_questions:
        return None
    
    # 获取学生已做过的题目ID
    answered_question_ids = set()
    for history in student_data.get('answer_history', []):
        answered_question_ids.add(history.get('question_id'))
    
    # 过滤出学生未做过的题目
    available_questions = [q for q in node_questions if q.get('id') not in answered_question_ids]
    
    if not available_questions:
        return None
    
    # 随机选择一道题目
    return random.choice(available_questions)
