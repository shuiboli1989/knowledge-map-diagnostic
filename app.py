"""Streamlit 主应用入口

该模块是整个教育诊断系统的前端界面入口，
使用 Streamlit 框架实现用户交互界面，
包括侧边栏和主区域的布局。
"""

import streamlit as st
import re
from pathlib import Path
from core.initializer import create_student_state, record_answer
from core.bkt import update_student_state
from core.cat import select_next_node, select_next_question
from utils.io import load_json, save_student, load_student
from pyvis.network import Network
import tempfile

# 设置页面标题
st.set_page_config(
    page_title="智学诊断 · 金融学基础",
    page_icon="📚",
    layout="wide"
)

# 注入全局 CSS 样式
st.markdown("""
<style>
/* 全局样式 */
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    background-color: #F5F5F5;
    color: #1A1A1A;
}

/* 页面最大宽度限制 */
.main > div {
    max-width: 1100px;
    margin: 0 auto;
}

/* 卡片样式 */
.card {
    background-color: #FFFFFF;
    border-radius: 8px;
    border: 1px solid #EEEEEE;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    padding: 20px;
    margin-bottom: 20px;
}

/* 去除 Streamlit 默认 footer */
footer {
    display: none !important;
}

/* 隐藏 header 中的品牌信息，但保留侧边栏控制按钮 */
header .css-18ni7ap {
    display: none !important;
}

/* 按钮样式 */
.stButton > button {
    background-color: #D42B2B;
    color: white;
    border-radius: 6px;
    border: none;
    padding: 8px 16px;
    font-weight: 500;
    width: 100%;
    height: 40px;
}

.stButton > button:hover {
    background-color: #B52020;
    color: white;
}

/* 次按钮样式 */
.stButton > button.secondary {
    background-color: white;
    color: #D42B2B;
    border: 1px solid #D42B2B;
}

.stButton > button.secondary:hover {
    background-color: #FFF0F0;
    color: #B52020;
}

/* 进度条样式 */
.stProgress > div > div {
    border-radius: 2px;
}

/* 侧边栏样式 */
[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #EEEEEE;
}

.stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar h4, .stSidebar h5, .stSidebar h6 {
    color: #1A1A1A !important;
    font-weight: bold;
}

.stSidebar p, .stSidebar div {
    color: #1A1A1A !important;
}

.stSidebar .stTextInput > div > div > input {
    background-color: white;
    border-radius: 6px;
    border: 1px solid #EEEEEE;
    padding: 8px;
}

/* 自定义选项样式 */
.custom-option {
    padding: 10px 15px;
    border: 1px solid #EEEEEE;
    border-radius: 6px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: all 0.2s ease;
    height: 40px;
    line-height: 20px;
    background-color: #F9F9F9;
}

.custom-option:hover {
    border-color: #D42B2B;
}

.custom-option.selected {
    background-color: #FFF0F0;
    border-color: #D42B2B;
    border-width: 1.5px;
}

/* 反馈卡片样式 */
.feedback-card {
    padding: 20px;
    border-radius: 8px;
    margin-top: 20px;
}

.feedback-card.correct {
    background-color: #F0FDF4;
    border-left: 4px solid #15803D;
}

.feedback-card.incorrect {
    background-color: #F5F5F5;
    border-left: 4px solid #CCCCCC;
}

/* 题目卡片 */
.question-card {
    background-color: #FFFFFF;
    border-radius: 8px;
    border: 1px solid #EEEEEE;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    padding: 20px;
    margin-bottom: 20px;
    border-left: 4px solid #D42B2B;
}

/* 标签样式 */
.tag {
    background-color: #FFF0F0;
    color: #D42B2B;
    border-radius: 12px;
    padding: 4px 12px;
    font-size: 11px;
    display: inline-block;
    margin-right: 8px;
    margin-bottom: 8px;
}

/* 概率变化显示 */
.probability-change {
    font-size: 16px;
    font-weight: bold;
}

.probability-old {
    color: #666666;
}

.probability-arrow {
    color: #CCCCCC;
    margin: 0 8px;
}

.probability-new {
    font-weight: bold;
}

/* 数字统计 */
.stat-number {
    font-size: 24px;
    font-weight: bold;
    color: #D42B2B;
}

.stat-label {
    font-size: 12px;
    color: #666666;
}
</style>
""", unsafe_allow_html=True)

# 侧边栏
# 顶部品牌区域
st.sidebar.markdown("""
<div style='padding: 20px 0; border-bottom: 1px solid #EEEEEE; margin-bottom: 20px;'>
    <h1 style='font-size: 18px; font-weight: bold; color: #1A1A1A; margin: 0; padding-left: 12px; border-left: 4px solid #D42B2B;'>教育诊断系统</h1>
</div>
""", unsafe_allow_html=True)

# 学生信息
student_id = st.sidebar.text_input("学生ID", placeholder="请输入学生ID")

# 课程选择
courses = {
    "course_finance_101": "金融学基础",
    "course_linear_algebra": "线性代数",
    "course_china_finance": "中国金融学"
}

# 初始化 session_state 中的课程ID
if 'last_course_id' not in st.session_state:
    st.session_state.last_course_id = None

course_id = st.sidebar.selectbox("选择课程", options=list(courses.keys()), format_func=lambda x: courses[x])
st.sidebar.markdown(f"<p style='color: #1A1A1A;'>课程: {courses[course_id]}</p>", unsafe_allow_html=True)

# 当课程发生变化时，重置 session_state 中的题目相关变量
if st.session_state.last_course_id != course_id:
    st.session_state.current_question = None
    st.session_state.answered = False
    st.session_state.selected_option = None
    st.session_state.p_mastery_before = 0
    st.session_state.last_course_id = course_id
    st.rerun()

# 加载知识图谱和题库
graph_path = Path(__file__).parent / "data" / f"graph_{course_id}.json"
questions_path = Path(__file__).parent / "data" / f"questions_{course_id}.json"

# 如果课程文件不存在，使用默认的金融学基础数据
if not graph_path.exists():
    graph_path = Path(__file__).parent / "data" / "graph.json"
if not questions_path.exists():
    questions_path = Path(__file__).parent / "data" / "questions.json"

try:
    graph_data = load_json(graph_path)
    questions_data = load_json(questions_path)
    # 检查 questions_data 的类型
    if isinstance(questions_data, list):
        # 如果是数组，直接使用
        questions = questions_data
    else:
        # 如果是对象，获取 'questions' 字段
        questions = questions_data.get('questions', [])
except Exception as e:
    st.error(f"加载数据文件失败: {e}")
    graph_data = {"nodes": []}
    questions = []

# 初始化学生状态
if student_id:
    # 尝试加载学生状态（指定课程ID）
    student_data = load_student(student_id, course_id)
    
    # 如果学生状态不存在或 node_states 为空，创建新状态
    if not student_data or not student_data.get('node_states', {}):
        student_data = create_student_state(student_id, course_id, graph_data)
        save_student(student_data)
        st.sidebar.success("学生状态已初始化")
    
    # 显示当前各节点掌握概率
    st.sidebar.markdown("<h3 style='color: #1A1A1A;'>知识点掌握情况</h3>", unsafe_allow_html=True)
    for node in graph_data.get('nodes', []):
        node_id = node.get('id')
        node_name = node.get('name', node_id)
        if node_id in student_data['node_states']:
            p_mastery = student_data['node_states'][node_id].get('p_mastery', 0)
            # 根据掌握程度设置颜色
            if p_mastery > 0.6:
                color = "#15803D"
            elif p_mastery > 0.3:
                color = "#FF9500"
            else:
                color = "#CCCCCC"
            # 显示知识点行
            st.sidebar.markdown(f"""
            <div style='display: flex; flex-direction: column; margin-bottom: 12px;'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;'>
                    <span style='font-size: 12px; color: #1A1A1A;'>{node_name}</span>
                    <span style='font-size: 12px; font-weight: bold; color: {color};'>{p_mastery * 100:.0f}%</span>
                </div>
                <div style='width: 100%; height: 4px; background-color: #F5F5F5; border-radius: 2px; overflow: hidden;'>
                    <div style='width: {p_mastery * 100}%; height: 100%; background-color: {color}; border-radius: 2px;'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# 主区域
tab1, tab2 = st.tabs(["自适应诊断", "知识图谱"])

with tab1:
    st.subheader("自适应诊断")
    
    if not student_id:
        st.warning("请在侧边栏输入学生ID")
    else:
        # 初始化 session_state
        if 'current_question' not in st.session_state:
            st.session_state.current_question = None
        if 'answered' not in st.session_state:
            st.session_state.answered = False
        if 'selected_option' not in st.session_state:
            st.session_state.selected_option = None
        if 'p_mastery_before' not in st.session_state:
            st.session_state.p_mastery_before = 0
        
        # 加载学生状态
        student_data = load_student(student_id, course_id)
        
        # 确保学生状态存在
        if not student_data:
            student_data = create_student_state(student_id, course_id, graph_data)
            save_student(student_data)
        
        # 选择下一题
        def get_next_question():
            with st.spinner("正在为你选题..."):
                # 选择下一个节点
                node_id = select_next_node(graph_data, student_data, questions)
                if not node_id:
                    st.error("没有可用的题目")
                    return None
                
                # 从选中节点选择题目
                question = select_next_question(node_id, student_data, questions)
                if not question:
                    st.error("该知识点没有可用的题目")
                    return None
                
                return question
        
        # 初始化或获取当前题目
        if not st.session_state.current_question:
            st.session_state.current_question = get_next_question()
        
        # 显示当前题目
        if st.session_state.current_question:
            question = st.session_state.current_question
            node_id = question.get('node_id')
            level = question.get('level', '')
            
            # 获取知识点名称
            node_name = ""
            for node in graph_data.get('nodes', []):
                if node.get('id') == node_id:
                    node_name = node.get('name', node_id)
                    break
            
            # 记录答题前的掌握概率
            st.session_state.p_mastery_before = student_data['node_states'].get(node_id, {}).get('p_mastery', 0)
            
            # 认知层次英文转中文
            level_map = {
                'memory': '记忆',
                'understanding': '理解',
                'application': '应用',
                'analysis': '分析'
            }
            chinese_level = level_map.get(level, level)
            
            # 为认知层次标签设置不同的颜色
            level_colors = {
                '记忆': '#4F46E5',  # 紫色
                '理解': '#10B981',  # 绿色
                '应用': '#F59E0B',  # 橙色
                '分析': '#EF4444'   # 红色
            }
            level_color = level_colors.get(chinese_level, '#666666')
            
            # 题型标注（假设为单选题）
            question_type = "单选题"
            
            # 处理行列式的显示，使用 LaTeX 渲染
            question_text = question.get('question')
            
            # 检查是否包含行列式
            if '|' in question_text:
                # 简单处理：将 |a b; c d| 格式转换为 LaTeX 格式
                # 匹配二阶行列式
                question_text = re.sub(r'\|(.*?);\s*(.*?)\|', r'$\\begin{vmatrix}\1 \\cr \\2\\end{vmatrix}$', question_text)
                # 匹配三阶行列式
                question_text = re.sub(r'\|(.*?);\s*(.*?);\s*(.*?)\|', r'$\\begin{vmatrix}\1 \\cr \\2 \\cr \\3\\end{vmatrix}$', question_text)
            
            # 处理矩阵的显示，使用 LaTeX 渲染
            if '[' in question_text and ']' in question_text:
                # 简单处理：将 [[a, b], [c, d]] 格式转换为 LaTeX 格式
                question_text = re.sub(r'\[\[(.*?),\s*(.*?)\],\s*\[(.*?),\s*(.*?)\]\]', r'$\\begin{bmatrix} \1 & \2 \\ \3 & \4 \\ \end{bmatrix}$', question_text)
            
            # 显示题目卡片
            st.markdown(f"""
            <div class="question-card">
                <div style="margin-bottom: 12px;">
                    <span class="tag">{node_name}</span>
                    <span style="background-color: #F0F9FF; color: {level_color}; border-radius: 12px; padding: 4px 12px; font-size: 11px; display: inline-block; margin-right: 8px; margin-bottom: 8px;">{chinese_level}</span>
                    <span style="background-color: #F0FDF4; color: #10B981; border-radius: 12px; padding: 4px 12px; font-size: 11px; display: inline-block; margin-right: 8px; margin-bottom: 8px;">{question_type}</span>
                </div>
                <h3 style="font-size: 16px; font-weight: bold; color: #1A1A1A; line-height: 1.6; margin-bottom: 20px;">题目: {question_text}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # 显示选项
            options = question.get('options', [])
            question_id = question.get('id', '')
            
            # 自定义选项样式
            for i, option in enumerate(options):
                is_selected = st.session_state.selected_option == option
                option_html = f"""
                <div class="custom-option {'selected' if is_selected else ''}">
                    {option}
                </div>
                """
                if st.checkbox(option, value=is_selected, key=f"option_{question_id}_{i}"):
                    st.session_state.selected_option = option
            
            # 提交按钮
            if not st.session_state.answered:
                if st.button("提交答案", key="submit") and st.session_state.selected_option:
                    # 检查答案是否正确
                    correct_answer = question.get('answer')
                    is_correct = st.session_state.selected_option.startswith(correct_answer)
                    
                    # 记录答题
                    student_data = record_answer(student_data, node_id, question.get('id'), is_correct)
                    
                    # 更新掌握概率
                    student_data = update_student_state(student_data, node_id, is_correct)
                    
                    # 保存学生状态
                    save_student(student_data)
                    
                    # 显示答案解析和概率变化
                    st.session_state.answered = True
                    
                    # 显示答案解析
                    feedback_class = "correct" if is_correct else "incorrect"
                    feedback_title = "✓ 回答正确" if is_correct else "✗ 回答错误"
                    feedback_title_color = "#15803D" if is_correct else "#666666"
                    
                    # 获取答题后的掌握概率
                    p_mastery_after = student_data['node_states'].get(node_id, {}).get('p_mastery', 0)
                    # 根据掌握程度设置颜色
                    if p_mastery_after > 0.6:
                        new_prob_color = "#15803D"
                    elif p_mastery_after > 0.3:
                        new_prob_color = "#FF9500"
                    else:
                        new_prob_color = "#CCCCCC"
                    
                    st.markdown(f"""
                    <div class="feedback-card {feedback_class}">
                        <h3 style="margin-top: 0; font-size: 14px; font-weight: bold; color: {feedback_title_color};">{feedback_title}</h3>
                        <p style="font-size: 12px; color: #1A1A1A;"><strong>正确答案:</strong> {correct_answer}</p>
                        <p style="font-size: 12px; color: #1A1A1A;"><strong>你的答案:</strong> {st.session_state.selected_option[0]}</p>
                        <p style="font-size: 12px; color: #1A1A1A;"><strong>解析:</strong> {question.get('explanation', '无解析')}</p>
                        <h4 style="font-size: 12px; color: #666666; margin-top: 16px;">掌握概率变化</h4>
                        <div class="probability-change">
                            <span class="probability-old">{st.session_state.p_mastery_before * 100:.0f}%</span>
                            <span class="probability-arrow">→</span>
                            <span class="probability-new" style="color: {new_prob_color};">{p_mastery_after * 100:.0f}%</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # 下一题按钮
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("下一题", key="next"):
                        st.session_state.current_question = get_next_question()
                        st.session_state.answered = False
                        st.session_state.selected_option = None
                        st.rerun()
        else:
            st.info("没有可用的题目")

with tab2:
    st.subheader("知识图谱")
    
    if not student_id:
        st.warning("请在侧边栏输入学生ID")
    else:
        # 加载学生状态
        student_data = load_student(student_id, course_id)
        
        # 确保学生状态存在
        if not student_data:
            student_data = create_student_state(student_id, course_id, graph_data)
            save_student(student_data)
        
        # 生成知识图谱可视化
        st.markdown("### 知识点关联与掌握情况")
        
        # 创建 pyvis 网络
        net = Network(height='700px', width='100%', directed=True)
        
        # 设置非层次化布局，自动居中
        net.set_options("""
        var options = {
          "layout": {
            "hierarchical": {
              "enabled": false
            }
          },
          "edges": {
            "color": {
              "color": "#DDDDDD",
              "highlight": "#D42B2B"
            },
            "arrows": {
              "to": {
                "enabled": true
              }
            }
          },
          "nodes": {
            "font": {
              "size": 14,
              "face": "Arial",
              "color": "#FFFFFF",
              "strokeWidth": 1,
              "strokeColor": "#000000"
            },
            "shape": "circle",
            "borderWidth": 2,
            "shadow": {
              "enabled": true,
              "size": 5,
              "x": 0,
              "y": 0,
              "color": "rgba(0,0,0,0.3)"
            }
          },
          "interaction": {
            "hover": true,
            "tooltipDelay": 200,
            "zoomView": true,
            "dragNodes": true,
            "dragView": true,
            "zoomSpeed": 1.2
          },
          "physics": {
            "enabled": true,
            "stabilization": {
              "enabled": true,
              "iterations": 1000,
              "updateInterval": 50,
              "onlyDynamicEdges": false,
              "fit": true
            },
            "barnesHut": {
              "gravitationalConstant": -80000,
              "centralGravity": 0.3,
              "springLength": 100,
              "springConstant": 0.04,
              "damping": 0.09
            }
          }
        }
        """)
        
        # 先添加所有节点，无论是否在 student_data 中
        for node in graph_data.get('nodes', []):
            node_id = node.get('id')
            node_name = node.get('name', node_id)
            # 检查节点是否在学生状态中
            if node_id in student_data['node_states']:
                p_mastery = student_data['node_states'][node_id].get('p_mastery', 0)
                # 根据掌握程度设置颜色
                if p_mastery > 0.6:
                    # 已掌握：填充 #15803D，白色文字
                    color = "#15803D"
                    font_color = "#FFFFFF"
                    border_color = "#15803D"
                elif p_mastery > 0.3:
                    # 学习中：填充 #FF9500，白色文字
                    color = "#FF9500"
                    font_color = "#FFFFFF"
                    border_color = "#FF9500"
                else:
                    # 待加强：填充 #F5F5F5，文字 #666666，边框 #DDDDDD
                    color = "#F5F5F5"
                    font_color = "#666666"
                    border_color = "#DDDDDD"
                # 节点标签显示节点名称和掌握概率百分比
                label = f"{node_name}\n{p_mastery * 100:.0f}%"
            else:
                # 节点不在学生状态中，使用默认颜色
                color = "#F5F5F5"
                font_color = "#666666"
                border_color = "#DDDDDD"
                label = f"{node_name}\n0%"
            # 添加节点，设置大小为 30
            net.add_node(node_id, label=label, size=30, color=color, font={"color": font_color, "size": 14, "face": "Arial", "strokeWidth": 1, "strokeColor": "#000000"}, borderWidth=2, borderColor=border_color)

        # 添加边（先修关系）
        for node in graph_data.get('nodes', []):
            node_id = node.get('id')
            prerequisites = node.get('prerequisites', [])
            for prereq_id in prerequisites:
                # 检查源节点是否存在
                if prereq_id in [node['id'] for node in graph_data.get('nodes', [])]:
                    # 添加有向边，方向为先修节点 → 后继节点
                    net.add_edge(prereq_id, node_id, color="#DDDDDD")
        
        # 生成 HTML 文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            net.write_html(f.name)
            temp_file = f.name
        
        # 读取 HTML 内容
        with open(temp_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 嵌入 HTML 到 Streamlit
        st.components.v1.html(html_content, height=700)
