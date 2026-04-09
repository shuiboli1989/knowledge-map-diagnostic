"""问卷模块单元测试"""

import pytest
from core.survey import (
    get_modules, apply_survey, get_anchor_modules, apply_anchor_result,
    FAMILIARITY_MULTIPLIERS, ANCHOR_THRESHOLD
)


GRAPH_DATA = {
    "modules": [
        {
            "id": "mod_01",
            "name": "模块1",
            "node_ids": ["n1", "n2"],
            "representative_node_id": "n1"
        },
        {
            "id": "mod_02",
            "name": "模块2",
            "node_ids": ["n3"],
            "representative_node_id": "n3"
        }
    ],
    "nodes": [
        {"id": "n1", "name": "知识点1", "prerequisites": [], "difficulty_coeff": 0.5},
        {"id": "n2", "name": "知识点2", "prerequisites": ["n1"], "difficulty_coeff": 0.6},
        {"id": "n3", "name": "知识点3", "prerequisites": ["n1"], "difficulty_coeff": 0.5}
    ]
}


def make_student():
    return {
        "student_id": "stu_test",
        "course_id": "test",
        "node_states": {
            "n1": {"p_mastery": 0.5, "answered_count": 0},
            "n2": {"p_mastery": 0.4, "answered_count": 0},
            "n3": {"p_mastery": 0.5, "answered_count": 0}
        },
        "answer_history": []
    }


def test_get_modules():
    assert len(get_modules(GRAPH_DATA)) == 2
    assert get_modules({"nodes": []}) == []


def test_apply_survey_boost():
    """自评'掌握较好'应提升概率"""
    s = make_student()
    responses = {"mod_01": 3, "mod_02": 0}
    s = apply_survey(s, GRAPH_DATA, responses)
    # mod_01 节点应被提升 (×1.5)
    assert s["node_states"]["n1"]["p_mastery"] == round(0.5 * 1.5, 4)
    assert s["node_states"]["n2"]["p_mastery"] == round(0.4 * 1.5, 4)
    # mod_02 节点应被下调 (×0.6)
    assert s["node_states"]["n3"]["p_mastery"] == round(0.5 * 0.6, 4)
    assert s["survey_results"]["completed"] is True


def test_apply_survey_clamp():
    """概率不应超过 MASTERY_THRESHOLD - 0.01"""
    s = make_student()
    s["node_states"]["n1"]["p_mastery"] = 0.9
    responses = {"mod_01": 3}  # ×1.5 → 1.35, should clamp to 0.94
    s = apply_survey(s, GRAPH_DATA, responses)
    assert s["node_states"]["n1"]["p_mastery"] == 0.94


def test_get_anchor_modules():
    responses = {"mod_01": 3, "mod_02": 1}
    anchors = get_anchor_modules(responses)
    assert "mod_01" in anchors
    assert "mod_02" not in anchors


def test_apply_anchor_correct():
    """锚点答对不改变概率"""
    s = make_student()
    s["survey_results"] = {"completed": True, "responses": {}, "anchor_tests": {}}
    p_before = s["node_states"]["n1"]["p_mastery"]
    s = apply_anchor_result(s, GRAPH_DATA, "mod_01", True)
    assert s["node_states"]["n1"]["p_mastery"] == p_before
    assert s["survey_results"]["anchor_tests"]["mod_01"]["is_correct"] is True


def test_apply_anchor_wrong():
    """锚点答错应降低该模块所有节点概率"""
    s = make_student()
    s["survey_results"] = {"completed": True, "responses": {}, "anchor_tests": {}}
    s = apply_anchor_result(s, GRAPH_DATA, "mod_01", False)
    assert s["node_states"]["n1"]["p_mastery"] == round(0.5 * 0.5, 4)
    assert s["node_states"]["n2"]["p_mastery"] == round(0.4 * 0.5, 4)
    # mod_02 不受影响
    assert s["node_states"]["n3"]["p_mastery"] == 0.5
