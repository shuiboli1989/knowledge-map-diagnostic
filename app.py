"""Streamlit 主应用入口

该模块是整个教育诊断系统的前端界面入口，
使用 Streamlit 框架实现用户交互界面，
包括侧边栏和主区域的布局。
"""

import streamlit as st
from pathlib import Path
from core.initializer import create_student_state, record_answer
from core.bkt import update_student_state
from core.cat import select_next_node, select_next_question, MASTERY_THRESHOLD
from core.survey import get_modules, apply_survey, get_anchor_modules, apply_anchor_result, FAMILIARITY_LABELS
from core.learning_path import generate_full_path, generate_target_path, get_current_node, advance_path
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
    "course_china_finance": "中国金融学",
    "course_philosophy": "哲学通论"
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

    # ========== 入学问卷流程 ==========
    modules = get_modules(graph_data)
    has_survey = student_data.get('survey_results') is not None

    # 初始化问卷相关 session_state
    if 'survey_step' not in st.session_state:
        st.session_state.survey_step = "done" if has_survey else ("survey" if modules else "done")
    # 课程切换时重置问卷状态
    if has_survey:
        st.session_state.survey_step = "done"

    if st.session_state.survey_step == "survey" and modules:
        st.subheader("入学问卷")
        st.markdown("请根据你的实际情况，评估对以下各模块的熟悉程度：")

        with st.form("survey_form"):
            responses = {}
            for mod in modules:
                level = st.radio(
                    mod['name'],
                    options=[0, 1, 2, 3],
                    format_func=lambda x: FAMILIARITY_LABELS[x],
                    horizontal=True,
                    key=f"survey_{mod['id']}"
                )
                responses[mod['id']] = level

            submitted = st.form_submit_button("提交问卷")
            if submitted:
                student_data = apply_survey(student_data, graph_data, responses)
                save_student(student_data)

                # 检查是否需要锚点测试
                anchor_mods = get_anchor_modules(responses)
                if anchor_mods:
                    st.session_state.survey_step = "anchor"
                    st.session_state.anchor_queue = anchor_mods
                    st.session_state.anchor_index = 0
                    st.session_state.anchor_answered = False
                else:
                    st.session_state.survey_step = "done"
                st.rerun()
        st.stop()

    elif st.session_state.survey_step == "anchor" and modules:
        anchor_queue = st.session_state.get('anchor_queue', [])
        anchor_idx = st.session_state.get('anchor_index', 0)

        if anchor_idx >= len(anchor_queue):
            st.session_state.survey_step = "done"
            st.rerun()
        else:
            current_mod_id = anchor_queue[anchor_idx]
            # 找到模块信息
            current_mod = None
            for m in modules:
                if m['id'] == current_mod_id:
                    current_mod = m
                    break

            if current_mod:
                st.subheader("锚点验证测试")
                st.markdown(f"你自评对 **{current_mod['name']}** 有基础，现在验证一下：")
                st.markdown(f"*（{anchor_idx + 1}/{len(anchor_queue)}）*")

                # 从代表性节点选一道题
                rep_node_id = current_mod.get('representative_node_id')
                anchor_q = select_next_question(rep_node_id, student_data, questions)

                if anchor_q and not st.session_state.get('anchor_answered', False):
                    st.markdown(f"**题目：** {anchor_q.get('question', '')}")
                    options = anchor_q.get('options', [])
                    selected = st.radio("选择答案", options, index=None, key=f"anchor_radio_{anchor_idx}", label_visibility="collapsed")

                    if st.button("提交验证", key=f"anchor_submit_{anchor_idx}") and selected:
                        correct_answer = anchor_q.get('answer', '')
                        is_correct = selected.startswith(correct_answer)
                        student_data = apply_anchor_result(student_data, graph_data, current_mod_id, is_correct)
                        # 记录答题
                        student_data = record_answer(student_data, rep_node_id, anchor_q.get('id'), is_correct)
                        student_data = update_student_state(student_data, rep_node_id, is_correct)
                        save_student(student_data)

                        if is_correct:
                            st.success(f"验证通过！{current_mod['name']} 的掌握评估已确认。")
                        else:
                            st.warning(f"验证未通过，已下调 {current_mod['name']} 的掌握概率。")

                        st.session_state.anchor_index = anchor_idx + 1
                        st.session_state.anchor_answered = False
                        st.rerun()
                elif not anchor_q:
                    # 没有可用题目，跳过
                    st.session_state.anchor_index = anchor_idx + 1
                    st.rerun()
            else:
                st.session_state.anchor_index = anchor_idx + 1
                st.rerun()
        st.stop()

    # 侧边栏：重新做问卷按钮
    if has_survey and modules:
        if st.sidebar.button("重新做问卷", key="redo_survey"):
            st.session_state.survey_step = "survey"
            # 重置学生状态为初始值
            student_data = create_student_state(student_id, course_id, graph_data)
            student_data['survey_results'] = None
            student_data['learning_path'] = None
            save_student(student_data)
            st.rerun()

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
tab1, tab2, tab3 = st.tabs(["自适应诊断", "学习路径", "知识图谱"])

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

            question_text = question.get('question')

            # 显示题目卡片：标签部分用 HTML，题目文本用 st.markdown 以支持 LaTeX
            st.markdown(f"""
            <div class="question-card">
                <div style="margin-bottom: 12px;">
                    <span class="tag">{node_name}</span>
                    <span style="background-color: #F0F9FF; color: {level_color}; border-radius: 12px; padding: 4px 12px; font-size: 11px; display: inline-block; margin-right: 8px; margin-bottom: 8px;">{chinese_level}</span>
                    <span style="background-color: #F0FDF4; color: #10B981; border-radius: 12px; padding: 4px 12px; font-size: 11px; display: inline-block; margin-right: 8px; margin-bottom: 8px;">{question_type}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"**题目：** {question_text}")
            
            # 显示选项
            options = question.get('options', [])
            question_id = question.get('id', '')

            # 使用 radio 组件显示选项，支持 LaTeX 渲染
            selected = st.radio(
                "选择答案",
                options,
                index=None if not st.session_state.selected_option else (
                    options.index(st.session_state.selected_option) if st.session_state.selected_option in options else None
                ),
                key=f"radio_{question_id}",
                label_visibility="collapsed"
            )
            if selected:
                st.session_state.selected_option = selected
            
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
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown(f"**解析：** {question.get('explanation', '无解析')}")
                    st.markdown(f"""
                    <div style="margin-top: 8px;">
                        <h4 style="font-size: 12px; color: #666666;">掌握概率变化</h4>
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
    st.subheader("学习路径")

    if not student_id:
        st.warning("请在侧边栏输入学生ID")
    else:
        # 加载学生状态
        student_data = load_student(student_id, course_id)
        if not student_data:
            student_data = create_student_state(student_id, course_id, graph_data)
            save_student(student_data)

        modules = get_modules(graph_data)

        # 初始化学习路径 session_state
        if 'lp_question' not in st.session_state:
            st.session_state.lp_question = None
        if 'lp_answered' not in st.session_state:
            st.session_state.lp_answered = False
        if 'lp_selected' not in st.session_state:
            st.session_state.lp_selected = None

        # 模式选择
        path_mode = st.radio(
            "选择学习模式",
            ["全图谱通关", "指定目标模块"],
            horizontal=True,
            key="path_mode"
        )

        target_node_ids = []
        if path_mode == "指定目标模块" and modules:
            selected_mods = st.multiselect(
                "选择目标模块",
                options=[m['id'] for m in modules],
                format_func=lambda x: next((m['name'] for m in modules if m['id'] == x), x),
                key="target_modules"
            )
            for m in modules:
                if m['id'] in selected_mods:
                    target_node_ids.extend(m['node_ids'])

        if st.button("生成学习路径", key="gen_path"):
            if path_mode == "全图谱通关":
                path_nodes = generate_full_path(graph_data, student_data)
                mode = "full"
                target_mods = []
            else:
                path_nodes = generate_target_path(graph_data, student_data, target_node_ids)
                mode = "target"
                target_mods = st.session_state.get('target_modules', [])

            student_data['learning_path'] = {
                'mode': mode,
                'target_modules': target_mods,
                'path_nodes': path_nodes,
                'current_index': 0
            }
            # 跳过已掌握的起始节点
            student_data = advance_path(student_data, graph_data)
            save_student(student_data)
            st.session_state.lp_question = None
            st.session_state.lp_answered = False
            st.session_state.lp_selected = None
            st.rerun()

        # 显示学习路径
        lp = student_data.get('learning_path')
        if lp and lp.get('path_nodes'):
            path_nodes = lp['path_nodes']
            current_idx = lp.get('current_index', 0)
            node_map = {n['id']: n['name'] for n in graph_data.get('nodes', [])}
            node_states = student_data.get('node_states', {})

            # 路径进度
            mastered_count = sum(
                1 for nid in path_nodes
                if node_states.get(nid, {}).get('p_mastery', 0) >= MASTERY_THRESHOLD
            )
            st.progress(mastered_count / len(path_nodes) if path_nodes else 0)
            st.markdown(f"进度：{mastered_count}/{len(path_nodes)} 个知识点已掌握")

            # 可视化学习路径图谱
            path_set = set(path_nodes)
            path_order = {nid: i + 1 for i, nid in enumerate(path_nodes)}
            current_node_id = get_current_node(student_data)

            lp_net = Network(height='500px', width='100%', directed=True)
            lp_net.set_options("""
            var options = {
              "layout": {"hierarchical": {"enabled": false}},
              "edges": {
                "color": {"color": "#DDDDDD", "highlight": "#D42B2B"},
                "arrows": {"to": {"enabled": true}}
              },
              "nodes": {
                "font": {"size": 14, "face": "Arial", "color": "#FFFFFF", "strokeWidth": 1, "strokeColor": "#000000"},
                "shape": "circle",
                "borderWidth": 2,
                "shadow": {"enabled": true, "size": 5, "x": 0, "y": 0, "color": "rgba(0,0,0,0.3)"}
              },
              "interaction": {"hover": true, "tooltipDelay": 200, "zoomView": true, "dragNodes": true, "dragView": true},
              "physics": {
                "enabled": true,
                "stabilization": {"enabled": true, "iterations": 1000, "updateInterval": 50, "fit": true},
                "barnesHut": {"gravitationalConstant": -80000, "centralGravity": 0.3, "springLength": 100, "springConstant": 0.04, "damping": 0.09}
              }
            }
            """)

            all_node_ids = set()
            for node in graph_data.get('nodes', []):
                nid = node.get('id')
                all_node_ids.add(nid)
                node_name = node.get('name', nid)
                p = node_states.get(nid, {}).get('p_mastery', 0)

                if nid in path_set:
                    order_num = path_order[nid]
                    if p >= MASTERY_THRESHOLD:
                        # 已掌握的路径节点：绿色 + 勾号
                        color = "#15803D"
                        font_color = "#FFFFFF"
                        border_color = "#0D5C2A"
                        label = f"✓ {order_num}. {node_name}\n{p*100:.0f}%"
                        border_width = 3
                        size = 35
                    elif nid == current_node_id:
                        # 当前节点：红色高亮
                        color = "#D42B2B"
                        font_color = "#FFFFFF"
                        border_color = "#A01E1E"
                        label = f"▶ {order_num}. {node_name}\n{p*100:.0f}%"
                        border_width = 4
                        size = 40
                    else:
                        # 待学习的路径节点：橙色
                        color = "#FF9500"
                        font_color = "#FFFFFF"
                        border_color = "#CC7700"
                        label = f"{order_num}. {node_name}\n{p*100:.0f}%"
                        border_width = 3
                        size = 35
                else:
                    if p >= MASTERY_THRESHOLD:
                        # 非路径但已掌握的节点：绿色（小尺寸）
                        color = "#15803D"
                        font_color = "#FFFFFF"
                        border_color = "#0D5C2A"
                        label = f"✓ {node_name}\n{p*100:.0f}%"
                        border_width = 2
                        size = 28
                    else:
                        # 非路径未掌握节点：灰色
                        color = "#E8E8E8"
                        font_color = "#AAAAAA"
                        border_color = "#DDDDDD"
                        label = f"{node_name}\n{p*100:.0f}%"
                        border_width = 1
                        size = 22

                lp_net.add_node(nid, label=label, size=size, color=color,
                                font={"color": font_color, "size": 14, "face": "Arial", "strokeWidth": 1, "strokeColor": "#000000"},
                                borderWidth=border_width, borderColor=border_color)

            for node in graph_data.get('nodes', []):
                nid = node.get('id')
                for prereq_id in node.get('prerequisites', []):
                    if prereq_id in all_node_ids:
                        # 路径上的边用深色，其他用浅色
                        if nid in path_set and prereq_id in path_set:
                            edge_color = "#888888"
                            edge_width = 2
                        else:
                            edge_color = "#E0E0E0"
                            edge_width = 1
                        lp_net.add_edge(prereq_id, nid, color=edge_color, width=edge_width)

            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                lp_net.write_html(f.name)
                lp_temp = f.name
            with open(lp_temp, 'r', encoding='utf-8') as f:
                lp_html = f.read()
            st.components.v1.html(lp_html, height=520)

            # 图例
            st.markdown("""
            <div style="display: flex; gap: 20px; justify-content: center; margin: 8px 0 16px 0; font-size: 13px;">
                <span><span style="display:inline-block;width:14px;height:14px;border-radius:50%;background:#D42B2B;vertical-align:middle;margin-right:4px;"></span>当前学习</span>
                <span><span style="display:inline-block;width:14px;height:14px;border-radius:50%;background:#FF9500;vertical-align:middle;margin-right:4px;"></span>待学习</span>
                <span><span style="display:inline-block;width:14px;height:14px;border-radius:50%;background:#15803D;vertical-align:middle;margin-right:4px;"></span>已掌握</span>
                <span><span style="display:inline-block;width:14px;height:14px;border-radius:50%;background:#E8E8E8;vertical-align:middle;margin-right:4px;"></span>不在路径中</span>
            </div>
            """, unsafe_allow_html=True)

            # 当前节点出题
            current_node = get_current_node(student_data)
            if current_node:
                current_name = node_map.get(current_node, current_node)
                st.markdown("---")
                st.markdown(f"#### 当前学习：{current_name}")

                # 获取题目
                if not st.session_state.lp_question:
                    st.session_state.lp_question = select_next_question(current_node, student_data, questions)
                    st.session_state.lp_answered = False
                    st.session_state.lp_selected = None

                lp_q = st.session_state.lp_question
                if lp_q:
                    st.markdown(f"**题目：** {lp_q.get('question', '')}")
                    options = lp_q.get('options', [])
                    lp_selected = st.radio(
                        "选择答案",
                        options,
                        index=None if not st.session_state.lp_selected else (
                            options.index(st.session_state.lp_selected) if st.session_state.lp_selected in options else None
                        ),
                        key=f"lp_radio_{lp_q.get('id', '')}",
                        label_visibility="collapsed"
                    )
                    if lp_selected:
                        st.session_state.lp_selected = lp_selected

                    if not st.session_state.lp_answered:
                        if st.button("提交答案", key="lp_submit") and st.session_state.lp_selected:
                            correct_answer = lp_q.get('answer', '')
                            is_correct = st.session_state.lp_selected.startswith(correct_answer)

                            student_data = record_answer(student_data, current_node, lp_q.get('id'), is_correct)
                            student_data = update_student_state(student_data, current_node, is_correct)

                            # 检查是否掌握，自动前进
                            p_after = student_data['node_states'].get(current_node, {}).get('p_mastery', 0)
                            if p_after >= MASTERY_THRESHOLD:
                                student_data = advance_path(student_data, graph_data)

                            save_student(student_data)
                            st.session_state.lp_answered = True

                            if is_correct:
                                st.success(f"回答正确！正确答案：{correct_answer}")
                            else:
                                st.error(f"回答错误。正确答案：{correct_answer}")
                            st.markdown(f"**解析：** {lp_q.get('explanation', '无解析')}")

                            if p_after >= MASTERY_THRESHOLD:
                                st.success(f"{current_name} 已掌握！")
                    else:
                        if st.button("下一题", key="lp_next"):
                            st.session_state.lp_question = None
                            st.session_state.lp_answered = False
                            st.session_state.lp_selected = None
                            st.rerun()
                else:
                    p_current = node_states.get(current_node, {}).get('p_mastery', 0)
                    st.warning(f"{current_name} 的题目已全部做完，但尚未达到掌握阈值（当前 {p_current*100:.0f}%，需要 95%）。")
                    col_retry, col_skip = st.columns(2)
                    with col_retry:
                        if st.button("重新练习本知识点", key="lp_retry"):
                            # 清除该节点的答题记录，让题目重新可用
                            student_data['answer_history'] = [
                                h for h in student_data.get('answer_history', [])
                                if h.get('node_id') != current_node
                            ]
                            save_student(student_data)
                            st.session_state.lp_question = None
                            st.session_state.lp_answered = False
                            st.session_state.lp_selected = None
                            st.rerun()
                    with col_skip:
                        if st.button("跳到下一个知识点", key="lp_skip"):
                            lp_data = student_data.get('learning_path', {})
                            lp_data['current_index'] = lp_data.get('current_index', 0) + 1
                            student_data = advance_path(student_data, graph_data)
                            save_student(student_data)
                            st.session_state.lp_question = None
                            st.session_state.lp_answered = False
                            st.session_state.lp_selected = None
                            st.rerun()
            else:
                st.success("恭喜！学习路径已全部完成！")
        elif not lp:
            st.info("请选择学习模式并生成学习路径。")

with tab3:
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
