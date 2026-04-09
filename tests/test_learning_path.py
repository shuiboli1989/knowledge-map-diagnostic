"""学习路径模块单元测试"""

import pytest
from core.learning_path import (
    topological_sort, generate_full_path, generate_target_path,
    get_current_node, advance_path
)


GRAPH_DATA = {
    "nodes": [
        {"id": "A", "name": "A", "prerequisites": []},
        {"id": "B", "name": "B", "prerequisites": ["A"]},
        {"id": "C", "name": "C", "prerequisites": ["A"]},
        {"id": "D", "name": "D", "prerequisites": ["B", "C"]},
        {"id": "E", "name": "E", "prerequisites": ["D"]}
    ]
}


def make_student(mastery_map=None):
    if mastery_map is None:
        mastery_map = {"A": 0.3, "B": 0.4, "C": 0.5, "D": 0.3, "E": 0.2}
    return {
        "student_id": "stu_test",
        "course_id": "test",
        "node_states": {
            nid: {"p_mastery": p, "answered_count": 0}
            for nid, p in mastery_map.items()
        },
        "answer_history": []
    }


def test_topological_sort():
    result = topological_sort(GRAPH_DATA)
    assert len(result) == 5
    # A must come before B and C
    assert result.index("A") < result.index("B")
    assert result.index("A") < result.index("C")
    # B and C must come before D
    assert result.index("B") < result.index("D")
    assert result.index("C") < result.index("D")
    # D must come before E
    assert result.index("D") < result.index("E")


def test_generate_full_path_all_unmastered():
    s = make_student()
    path = generate_full_path(GRAPH_DATA, s)
    assert path == ["A", "B", "C", "D", "E"]


def test_generate_full_path_some_mastered():
    s = make_student({"A": 0.96, "B": 0.4, "C": 0.96, "D": 0.3, "E": 0.2})
    path = generate_full_path(GRAPH_DATA, s)
    assert "A" not in path
    assert "C" not in path
    assert path == ["B", "D", "E"]


def test_generate_full_path_all_mastered():
    s = make_student({"A": 0.96, "B": 0.96, "C": 0.96, "D": 0.96, "E": 0.96})
    path = generate_full_path(GRAPH_DATA, s)
    assert path == []


def test_generate_target_path():
    """指定目标D，应包含A、B、C、D（E不需要）"""
    s = make_student()
    path = generate_target_path(GRAPH_DATA, s, ["D"])
    assert "E" not in path
    assert "A" in path and "B" in path and "C" in path and "D" in path
    # 拓扑序
    assert path.index("A") < path.index("D")


def test_generate_target_path_skip_mastered():
    """目标D，A已掌握，路径不含A"""
    s = make_student({"A": 0.96, "B": 0.4, "C": 0.5, "D": 0.3, "E": 0.2})
    path = generate_target_path(GRAPH_DATA, s, ["D"])
    assert "A" not in path
    assert "B" in path and "C" in path and "D" in path


def test_get_current_node():
    s = make_student()
    s["learning_path"] = {"path_nodes": ["A", "B", "C"], "current_index": 1}
    assert get_current_node(s) == "B"


def test_get_current_node_none():
    s = make_student()
    assert get_current_node(s) is None


def test_get_current_node_completed():
    s = make_student()
    s["learning_path"] = {"path_nodes": ["A", "B"], "current_index": 2}
    assert get_current_node(s) is None


def test_advance_path():
    s = make_student({"A": 0.96, "B": 0.4, "C": 0.5, "D": 0.3, "E": 0.2})
    s["learning_path"] = {"path_nodes": ["A", "B", "C", "D", "E"], "current_index": 0}
    s = advance_path(s, GRAPH_DATA)
    # A is mastered, should skip to B
    assert s["learning_path"]["current_index"] == 1


def test_advance_path_all_done():
    s = make_student({"A": 0.96, "B": 0.96, "C": 0.96, "D": 0.96, "E": 0.96})
    s["learning_path"] = {"path_nodes": ["A", "B", "C", "D", "E"], "current_index": 0}
    s = advance_path(s, GRAPH_DATA)
    assert s["learning_path"]["current_index"] == 5  # past end
