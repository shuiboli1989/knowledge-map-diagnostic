"""BKT 模块单元测试

该模块包含对 BKT 更新逻辑的单元测试，
验证贝叶斯知识追踪算法的正确性。
"""

import pytest
from core.bkt import update_mastery, update_student_state


def test_update_mastery_correct_increases():
    """测试答对后概率上升"""
    p_initial = 0.5
    p_after_correct = update_mastery(p_initial, True)
    assert p_after_correct > p_initial


def test_update_mastery_incorrect_decreases():
    """测试答错后概率下降"""
    p_initial = 0.5
    p_after_incorrect = update_mastery(p_initial, False)
    assert p_after_incorrect < p_initial


def test_update_mastery_five_correct_approaches_099():
    """测试连续答对5次后概率应接近0.99"""
    p = 0.5
    for _ in range(5):
        p = update_mastery(p, True)
    assert p >= 0.95  # 连续答对5次后概率应接近0.99


def test_update_mastery_bounds():
    """测试概率不超出 [0.01, 0.99] 边界"""
    # 测试上限
    p_near_1 = 0.98
    for _ in range(10):
        p_near_1 = update_mastery(p_near_1, True)
    assert p_near_1 <= 0.99
    
    # 测试下限
    p_near_0 = 0.02
    for _ in range(10):
        p_near_0 = update_mastery(p_near_0, False)
    assert p_near_0 >= 0.01


def test_update_student_state():
    """测试 update_student_state 函数"""
    student_data = {
        "student_id": "stu_001",
        "course_id": "course_finance_101",
        "node_states": {
            "node_001": {
                "p_mastery": 0.5,
                "base_prob": 0.50,
                "difficulty_coeff": 0.80,
                "answered_count": 0,
                "last_updated": "2026-03-23T00:00:00"
            }
        },
        "answer_history": []
    }
    
    # 测试答对的情况
    updated_data = update_student_state(student_data, "node_001", True)
    assert updated_data["node_states"]["node_001"]["p_mastery"] > 0.5
    assert updated_data["node_states"]["node_001"]["answered_count"] == 1
    
    # 测试答错的情况
    p_before_incorrect = updated_data["node_states"]["node_001"]["p_mastery"]
    updated_data = update_student_state(updated_data, "node_001", False)
    assert updated_data["node_states"]["node_001"]["p_mastery"] < p_before_incorrect
    assert updated_data["node_states"]["node_001"]["answered_count"] == 2
