"""initializer 模块单元测试

该模块包含对初始概率计算逻辑的单元测试，
验证知识点初始掌握概率计算的正确性。
"""

import pytest
from core.initializer import compute_base_prob, compute_initial_prob, initialize_all_nodes


def test_compute_base_prob():
    """测试 compute_base_prob 函数"""
    assert compute_base_prob(0) == 0.50
    assert compute_base_prob(1) == 0.35
    assert compute_base_prob(2) == 0.25
    assert compute_base_prob(3) == 0.15
    assert compute_base_prob(5) == 0.15


def test_compute_initial_prob():
    """测试 compute_initial_prob 函数"""
    # 无先修节点 + 难度系数0.8 → 期望结果 0.62
    assert compute_initial_prob(0.50, 0.8) == 0.62
    # 2个先修节点 + 难度系数0.45 → 期望结果 0.33
    assert compute_initial_prob(0.25, 0.45) == 0.33
    # 3个先修节点 + 难度系数0.25 → 期望结果 0.19
    assert compute_initial_prob(0.15, 0.25) == 0.19


def test_initialize_all_nodes():
    """测试 initialize_all_nodes 函数"""
    # 构建测试用的知识图谱数据
    test_graph = {
        "nodes": [
            {
                "id": "node_001",
                "name": "知识点1",
                "prerequisites": [],
                "difficulty_coeff": 0.8
            },
            {
                "id": "node_002",
                "name": "知识点2",
                "prerequisites": ["node_001", "node_003"],
                "difficulty_coeff": 0.45
            },
            {
                "id": "node_003",
                "name": "知识点3",
                "prerequisites": ["node_001", "node_004", "node_005"],
                "difficulty_coeff": 0.25
            }
        ]
    }
    
    expected = {
        "node_001": 0.62,
        "node_002": 0.33,
        "node_003": 0.19
    }
    
    result = initialize_all_nodes(test_graph)
    assert result == expected
