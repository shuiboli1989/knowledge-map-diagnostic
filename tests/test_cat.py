"""CAT 模块单元测试

该模块包含对 CAT 选题逻辑的单元测试，
验证自适应测试选题算法的正确性。
"""

import pytest
from core.cat import select_next_node, select_next_question


def test_select_next_node_basic():
    """测试基本的节点选择逻辑"""
    # 构建测试数据
    graph_data = {
        "nodes": [
            {
                "id": "node_001",
                "name": "知识点1",
                "prerequisites": []
            },
            {
                "id": "node_002",
                "name": "知识点2",
                "prerequisites": ["node_001"]
            },
            {
                "id": "node_003",
                "name": "知识点3",
                "prerequisites": ["node_001"]
            }
        ]
    }
    
    student_data = {
        "student_id": "stu_001",
        "course_id": "course_finance_101",
        "node_states": {
            "node_001": {
                "p_mastery": 0.5,  # 最接近 0.5，应该被选中
                "answered_count": 0
            },
            "node_002": {
                "p_mastery": 0.8,  # 离 0.5 较远
                "answered_count": 0
            },
            "node_003": {
                "p_mastery": 0.2,  # 离 0.5 较远
                "answered_count": 0
            }
        },
        "answer_history": []
    }
    
    questions = [
        {"id": "q_001", "node_id": "node_001"},
        {"id": "q_002", "node_id": "node_002"},
        {"id": "q_003", "node_id": "node_003"}
    ]
    
    # 测试选择结果
    selected_node = select_next_node(graph_data, student_data, questions)
    assert selected_node == "node_001"


def test_select_next_node_filter_answered():
    """测试过滤已答题数 >= 3 的节点"""
    # 构建测试数据
    graph_data = {
        "nodes": [
            {
                "id": "node_001",
                "name": "知识点1",
                "prerequisites": []
            },
            {
                "id": "node_002",
                "name": "知识点2",
                "prerequisites": ["node_001"]
            }
        ]
    }
    
    student_data = {
        "student_id": "stu_001",
        "course_id": "course_finance_101",
        "node_states": {
            "node_001": {
                "p_mastery": 0.5,  # 最接近 0.5，但已答题数 >= 3
                "answered_count": 3
            },
            "node_002": {
                "p_mastery": 0.6,  # 离 0.5 较远，但未达 3 次
                "answered_count": 0
            }
        },
        "answer_history": []
    }
    
    questions = [
        {"id": "q_001", "node_id": "node_001"},
        {"id": "q_002", "node_id": "node_002"}
    ]
    
    # 测试选择结果
    selected_node = select_next_node(graph_data, student_data, questions)
    assert selected_node == "node_002"


def test_select_next_node_successor_priority():
    """测试优先选择拥有最多未测试后继节点的节点"""
    # 构建测试数据
    graph_data = {
        "nodes": [
            {
                "id": "node_001",
                "name": "知识点1",
                "prerequisites": []
            },
            {
                "id": "node_002",
                "name": "知识点2",
                "prerequisites": ["node_001"]
            },
            {
                "id": "node_003",
                "name": "知识点3",
                "prerequisites": ["node_001"]
            },
            {
                "id": "node_004",
                "name": "知识点4",
                "prerequisites": ["node_002"]
            }
        ]
    }
    
    student_data = {
        "student_id": "stu_001",
        "course_id": "course_finance_101",
        "node_states": {
            "node_001": {
                "p_mastery": 0.5,  # 最接近 0.5，有 2 个未测试后继节点
                "answered_count": 0
            },
            "node_002": {
                "p_mastery": 0.52,  # 接近 0.5，有 1 个未测试后继节点
                "answered_count": 0
            },
            "node_003": {
                "p_mastery": 0.48,  # 接近 0.5，无未测试后继节点
                "answered_count": 0
            },
            "node_004": {
                "p_mastery": 0.7,  # 离 0.5 较远
                "answered_count": 0
            }
        },
        "answer_history": []
    }
    
    questions = [
        {"id": "q_001", "node_id": "node_001"},
        {"id": "q_002", "node_id": "node_002"},
        {"id": "q_003", "node_id": "node_003"},
        {"id": "q_004", "node_id": "node_004"}
    ]
    
    # 测试选择结果
    selected_node = select_next_node(graph_data, student_data, questions)
    assert selected_node == "node_001"


def test_select_next_node_no_available():
    """测试无可选节点的情况"""
    # 构建测试数据
    graph_data = {
        "nodes": [
            {
                "id": "node_001",
                "name": "知识点1",
                "prerequisites": []
            }
        ]
    }
    
    student_data = {
        "student_id": "stu_001",
        "course_id": "course_finance_101",
        "node_states": {
            "node_001": {
                "p_mastery": 0.5,
                "answered_count": 3  # 已答题数 >= 3
            }
        },
        "answer_history": []
    }
    
    questions = [
        {"id": "q_001", "node_id": "node_001"}
    ]
    
    # 测试选择结果
    selected_node = select_next_node(graph_data, student_data, questions)
    assert selected_node is None


def test_select_next_question_basic():
    """测试基本的题目选择逻辑"""
    # 构建测试数据
    student_data = {
        "student_id": "stu_001",
        "course_id": "course_finance_101",
        "node_states": {},
        "answer_history": []
    }
    
    questions = [
        {"id": "q_001", "node_id": "node_001", "question": "问题1"},
        {"id": "q_002", "node_id": "node_001", "question": "问题2"},
        {"id": "q_003", "node_id": "node_002", "question": "问题3"}
    ]
    
    # 测试选择结果
    selected_question = select_next_question("node_001", student_data, questions)
    assert selected_question is not None
    assert selected_question["node_id"] == "node_001"


def test_select_next_question_no_available():
    """测试无可用题的情况"""
    # 构建测试数据
    student_data = {
        "student_id": "stu_001",
        "course_id": "course_finance_101",
        "node_states": {},
        "answer_history": [
            {"question_id": "q_001"},
            {"question_id": "q_002"}
        ]
    }
    
    questions = [
        {"id": "q_001", "node_id": "node_001", "question": "问题1"},
        {"id": "q_002", "node_id": "node_001", "question": "问题2"}
    ]
    
    # 测试选择结果
    selected_question = select_next_question("node_001", student_data, questions)
    assert selected_question is None
