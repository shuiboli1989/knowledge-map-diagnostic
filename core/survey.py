"""入学问卷逻辑模块

根据学生对各模块的自评熟悉度调整初始掌握概率，
并通过锚点测试验证自评结果。
"""

from core.cat import MASTERY_THRESHOLD

FAMILIARITY_LABELS = {
    0: "没接触过",
    1: "听说过",
    2: "学过且有基础",
    3: "掌握较好"
}

FAMILIARITY_MULTIPLIERS = {
    0: 0.6,
    1: 0.8,
    2: 1.2,
    3: 1.5
}

ANCHOR_THRESHOLD = 2  # 自评 >= 此级别需要锚点测试
ANCHOR_DOWNGRADE = 0.5  # 锚点答错时的概率衰减系数


def get_modules(graph_data: dict) -> list[dict]:
    """从图谱数据中获取模块列表"""
    return graph_data.get('modules', [])


def apply_survey(student_data: dict, graph_data: dict, responses: dict[str, int]) -> dict:
    """根据问卷结果调整各节点的初始掌握概率

    Args:
        student_data: 学生数据
        graph_data: 知识图谱数据（含 modules）
        responses: 模块ID -> 熟悉度等级(0-3) 的映射

    Returns:
        dict: 调整后的学生数据
    """
    modules = get_modules(graph_data)
    node_states = student_data.get('node_states', {})

    for module in modules:
        mod_id = module['id']
        level = responses.get(mod_id, 1)  # 默认"听说过"
        multiplier = FAMILIARITY_MULTIPLIERS.get(level, 1.0)

        for node_id in module.get('node_ids', []):
            if node_id in node_states:
                old_p = node_states[node_id]['p_mastery']
                new_p = max(0.01, min(MASTERY_THRESHOLD - 0.01, old_p * multiplier))
                node_states[node_id]['p_mastery'] = round(new_p, 4)

    student_data['survey_results'] = {
        'completed': True,
        'responses': responses,
        'anchor_tests': {}
    }
    return student_data


def get_anchor_modules(responses: dict[str, int]) -> list[str]:
    """返回需要锚点测试的模块ID列表（自评 >= ANCHOR_THRESHOLD）"""
    return [mod_id for mod_id, level in responses.items() if level >= ANCHOR_THRESHOLD]


def apply_anchor_result(student_data: dict, graph_data: dict, module_id: str, is_correct: bool) -> dict:
    """根据锚点测试结果调整模块概率

    答错时将该模块所有节点的掌握概率乘以衰减系数。

    Args:
        student_data: 学生数据
        graph_data: 知识图谱数据
        module_id: 模块ID
        is_correct: 锚点测试是否答对

    Returns:
        dict: 调整后的学生数据
    """
    modules = get_modules(graph_data)
    node_states = student_data.get('node_states', {})

    if not is_correct:
        for module in modules:
            if module['id'] == module_id:
                for node_id in module.get('node_ids', []):
                    if node_id in node_states:
                        old_p = node_states[node_id]['p_mastery']
                        new_p = max(0.01, old_p * ANCHOR_DOWNGRADE)
                        node_states[node_id]['p_mastery'] = round(new_p, 4)
                break

    # 记录锚点测试结果
    if 'survey_results' not in student_data:
        student_data['survey_results'] = {'completed': True, 'responses': {}, 'anchor_tests': {}}
    student_data['survey_results']['anchor_tests'][module_id] = {
        'is_correct': is_correct
    }

    return student_data
