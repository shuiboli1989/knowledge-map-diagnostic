"""初始概率计算模块

该模块实现了知识点初始掌握概率的计算逻辑，
基于知识点的先修关系和难度系数，
为每个学生初始化知识状态。
"""


def compute_base_prob(prerequisite_count: int) -> float:
    """根据先修节点数量计算基础概率

    Args:
        prerequisite_count: 先修节点数量

    Returns:
        float: 基础概率
    """
    if prerequisite_count == 0:
        return 0.50
    elif prerequisite_count == 1:
        return 0.35
    elif prerequisite_count == 2:
        return 0.25
    else:  # 3个及以上先修节点
        return 0.15


def compute_initial_prob(base_prob: float, difficulty_coeff: float) -> float:
    """计算初始掌握概率

    Args:
        base_prob: 基础概率
        difficulty_coeff: 难度系数

    Returns:
        float: 初始掌握概率（保留两位小数）
    """
    initial_prob = 0.6 * base_prob + 0.4 * difficulty_coeff
    return round(initial_prob, 2)


def initialize_all_nodes(graph_data: dict) -> dict[str, float]:
    """初始化所有节点的初始掌握概率

    Args:
        graph_data: 知识图谱数据

    Returns:
        dict[str, float]: 节点ID到初始掌握概率的映射
    """
    node_probs = {}
    for node in graph_data.get('nodes', []):
        node_id = node.get('id')
        prerequisites = node.get('prerequisites', [])
        difficulty_coeff = node.get('difficulty_coeff', 0.5)
        
        base_prob = compute_base_prob(len(prerequisites))
        initial_prob = compute_initial_prob(base_prob, difficulty_coeff)
        node_probs[node_id] = initial_prob
    
    return node_probs


def create_student_state(student_id: str, course_id: str, graph_data: dict) -> dict:
    """为新学生创建初始状态文件

    Args:
        student_id: 学生ID
        course_id: 课程ID
        graph_data: 知识图谱数据

    Returns:
        dict: 学生初始状态
    """
    import datetime
    
    # 计算每个节点的初始概率
    node_probs = initialize_all_nodes(graph_data)
    
    # 构建 node_states
    node_states = {}
    for node in graph_data.get('nodes', []):
        node_id = node.get('id')
        prerequisites = node.get('prerequisites', [])
        difficulty_coeff = node.get('difficulty_coeff', 0.5)
        
        base_prob = compute_base_prob(len(prerequisites))
        
        node_states[node_id] = {
            "p_mastery": node_probs.get(node_id, 0.5),
            "base_prob": base_prob,
            "difficulty_coeff": difficulty_coeff,
            "answered_count": 0,
            "last_updated": datetime.datetime.now().isoformat()
        }
    
    # 构建学生状态
    student_state = {
        "student_id": student_id,
        "course_id": course_id,
        "node_states": node_states,
        "answer_history": []
    }
    
    return student_state


def record_answer(student_data: dict, node_id: str, question_id: str, is_correct: bool) -> dict:
    """记录一次答题，更新 answer_history 和对应节点的 answered_count、last_updated

    Args:
        student_data: 学生数据
        node_id: 知识点ID
        question_id: 题目ID
        is_correct: 是否正确

    Returns:
        dict: 更新后的学生数据
    """
    import datetime
    
    # 记录答题历史
    answer_record = {
        "question_id": question_id,
        "node_id": node_id,
        "is_correct": is_correct,
        "timestamp": datetime.datetime.now().isoformat()
    }
    student_data["answer_history"].append(answer_record)
    
    # 更新节点状态
    if node_id in student_data["node_states"]:
        node_state = student_data["node_states"][node_id]
        node_state["answered_count"] += 1
        node_state["last_updated"] = datetime.datetime.now().isoformat()
    
    return student_data

