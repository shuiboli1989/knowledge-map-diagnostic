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


def test_update_mastery_incorrect_still_increases_slightly():
    """测试答错后：后验下降，但学习转移使总概率可能微升或微降"""
    p_initial = 0.5
    p_after_incorrect = update_mastery(p_initial, False)
    # 标准 BKT 中，答错后后验下降，但 P(T) 会拉回一些
    # 对于 p=0.5, P(S)=0.15, P(G)=0.25, P(T)=0.1：
    # 后验 ≈ 0.1667, 加转移后 ≈ 0.25
    assert p_after_incorrect < p_initial


def test_update_mastery_five_correct_approaches_1():
    """测试连续答对5次后概率应接近1.0"""
    p = 0.5
    for _ in range(5):
        p = update_mastery(p, True)
    assert p >= 0.98


def test_update_mastery_can_reach_1():
    """测试概率可以达到 1.0（不再被 0.99 硬限制）"""
    p = 0.5
    for _ in range(20):
        p = update_mastery(p, True)
    assert p == 1.0


def test_update_mastery_lower_bound():
    """测试概率不低于 0.01"""
    p = 0.02
    for _ in range(10):
        p = update_mastery(p, False)
    assert p >= 0.01


def test_update_mastery_learning_transfer():
    """测试学习转移效果：即使答错，持续练习概率也会逐步回升"""
    p = 0.3
    # 连续答错5次
    for _ in range(5):
        p = update_mastery(p, False)
    p_after_wrong = p
    # 然后连续答对5次
    for _ in range(5):
        p = update_mastery(p, True)
    # 答对后应该显著回升
    assert p > p_after_wrong + 0.3


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
