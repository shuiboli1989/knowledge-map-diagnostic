"""JSON 文件读写工具模块

该模块提供了 JSON 文件的读取和写入功能，
使用 pathlib.Path 进行文件路径管理。
"""

from pathlib import Path
import json


def load_json(path: Path) -> dict:
    """读取 JSON 文件并返回其内容

    Args:
        path: JSON 文件的路径

    Returns:
        dict: JSON 文件的内容
    """
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(path: Path, data: dict) -> None:
    """将数据写入 JSON 文件

    Args:
        path: JSON 文件的路径
        data: 要写入的数据
    """
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_student(student_data: dict) -> None:
    """将学生状态保存到 data/students/{student_id}.json

    Args:
        student_data: 学生数据
    """
    student_id = student_data.get('student_id')
    if not student_id:
        raise ValueError("student_data must contain 'student_id' field")
    
    # 构建文件路径
    students_dir = Path(__file__).parent.parent / "data" / "students"
    students_dir.mkdir(parents=True, exist_ok=True)
    file_path = students_dir / f"{student_id}.json"
    
    # 保存数据
    save_json(file_path, student_data)


def load_student(student_id: str) -> dict | None:
    """从文件加载学生状态，不存在时返回 None

    Args:
        student_id: 学生ID

    Returns:
        dict | None: 学生数据，不存在时返回 None
    """
    # 构建文件路径
    students_dir = Path(__file__).parent.parent / "data" / "students"
    file_path = students_dir / f"{student_id}.json"
    
    # 检查文件是否存在
    if not file_path.exists():
        return None
    
    # 加载数据
    return load_json(file_path)
