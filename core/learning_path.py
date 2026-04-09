"""学习路径生成模块

基于知识图谱的拓扑结构生成个性化学习路径，
支持全图谱通关和指定目标模块两种模式。
"""

from collections import deque
from core.cat import MASTERY_THRESHOLD


def topological_sort(graph_data: dict) -> list[str]:
    """对知识图谱进行拓扑排序（Kahn 算法）

    Returns:
        list[str]: 按先修关系排列的节点ID列表
    """
    nodes = graph_data.get('nodes', [])
    node_ids = [n['id'] for n in nodes]

    # 构建入度表和邻接表
    in_degree = {nid: 0 for nid in node_ids}
    successors = {nid: [] for nid in node_ids}
    prereq_set = set(node_ids)

    for node in nodes:
        nid = node['id']
        for prereq in node.get('prerequisites', []):
            if prereq in prereq_set:
                in_degree[nid] += 1
                successors[prereq].append(nid)

    # BFS
    queue = deque([nid for nid in node_ids if in_degree[nid] == 0])
    result = []

    while queue:
        nid = queue.popleft()
        result.append(nid)
        for succ in successors[nid]:
            in_degree[succ] -= 1
            if in_degree[succ] == 0:
                queue.append(succ)

    return result


def generate_full_path(graph_data: dict, student_data: dict) -> list[str]:
    """全图谱通关模式：拓扑排序后过滤已掌握节点"""
    sorted_nodes = topological_sort(graph_data)
    node_states = student_data.get('node_states', {})
    return [
        nid for nid in sorted_nodes
        if node_states.get(nid, {}).get('p_mastery', 0) < MASTERY_THRESHOLD
    ]


def generate_target_path(graph_data: dict, student_data: dict, target_node_ids: list[str]) -> list[str]:
    """指定目标模式：收集目标节点的所有前置依赖，过滤已掌握，拓扑排序

    Args:
        graph_data: 知识图谱数据
        student_data: 学生数据
        target_node_ids: 目标节点ID列表

    Returns:
        list[str]: 学习路径（含目标节点及其未掌握的前置节点）
    """
    nodes = graph_data.get('nodes', [])
    node_map = {n['id']: n for n in nodes}
    node_states = student_data.get('node_states', {})

    # BFS 反向收集所有前置节点
    needed = set(target_node_ids)
    queue = deque(target_node_ids)
    while queue:
        nid = queue.popleft()
        node = node_map.get(nid)
        if not node:
            continue
        for prereq in node.get('prerequisites', []):
            if prereq not in needed and prereq in node_map:
                needed.add(prereq)
                queue.append(prereq)

    # 拓扑排序后只保留需要的且未掌握的节点
    sorted_nodes = topological_sort(graph_data)
    return [
        nid for nid in sorted_nodes
        if nid in needed and node_states.get(nid, {}).get('p_mastery', 0) < MASTERY_THRESHOLD
    ]


def get_current_node(student_data: dict) -> str | None:
    """获取学习路径中的当前节点"""
    lp = student_data.get('learning_path')
    if not lp:
        return None
    path_nodes = lp.get('path_nodes', [])
    idx = lp.get('current_index', 0)
    if idx < len(path_nodes):
        return path_nodes[idx]
    return None


def advance_path(student_data: dict, graph_data: dict) -> dict:
    """当前节点掌握后前进到下一个未掌握的节点

    Returns:
        dict: 更新后的学生数据
    """
    lp = student_data.get('learning_path')
    if not lp:
        return student_data

    path_nodes = lp.get('path_nodes', [])
    node_states = student_data.get('node_states', {})
    idx = lp.get('current_index', 0)

    # 跳过已掌握的节点
    while idx < len(path_nodes):
        nid = path_nodes[idx]
        if node_states.get(nid, {}).get('p_mastery', 0) < MASTERY_THRESHOLD:
            break
        idx += 1

    lp['current_index'] = idx
    return student_data
