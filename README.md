# 教育诊断原型系统

## 项目简介

这是一个基于知识图谱的教育诊断原型系统，用于验证"基于知识图谱先验的冷启动个性化推荐"方案的可行性。系统通过贝叶斯知识追踪（BKT）模型和计算机化自适应测试（CAT）技术，为学生提供个性化的学习诊断和题目推荐。

## 技术栈

- **语言**：Python 3.10+
- **前端**：Streamlit
- **数据存储**：JSON 文件
- **LLM 调用**：直接调用 API
- **依赖库**：streamlit、requests、json、pathlib、pyvis

## 项目结构

```
project/
├── data/
│   ├── graph.json                      # 金融学基础知识图谱
│   ├── questions.json                  # 金融学基础题库
│   ├── graph_course_linear_algebra.json # 线性代数知识图谱
│   ├── questions_course_linear_algebra.json # 线性代数题库
│   └── students/                       # 学生状态文件
├── core/
│   ├── bkt.py                          # BKT 更新逻辑
│   ├── cat.py                          # CAT 选题逻辑
│   ├── initializer.py                  # 初始概率计算
│   └── llm_client.py                   # LLM API 调用封装
├── utils/
│   └── io.py                           # JSON 读写工具
├── tests/
│   ├── test_bkt.py
│   ├── test_cat.py
│   └── test_initializer.py
├── app.py                              # Streamlit 主入口
├── requirements.txt                    # 依赖文件
├── .gitignore                         # Git 忽略文件
└── validate_json.py                    # JSON 验证工具
```

## 核心功能

1. **多课程支持**：支持金融学基础和线性代数两门课程，可在侧边栏自由切换
2. **独立的课程状态**：每个学生可以拥有多个课程的状态，切换课程时不会覆盖之前的状态
3. **知识图谱可视化**：使用 pyvis 实现交互式知识图谱，展示知识点之间的先修关系和学生的掌握情况
4. **自适应诊断**：基于学生当前知识状态，自动选择信息增益最大的题目
5. **贝叶斯知识追踪**：根据学生答题情况动态更新知识点掌握概率
6. **冷启动初始化**：基于知识图谱的先修关系和知识点难度，计算初始掌握概率
7. **实时反馈**：答题后立即显示答案解析和掌握概率变化
8. **LaTeX 数学公式渲染**：支持矩阵、行列式等数学公式的正确显示

## 如何运行

1. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

2. 运行应用
   ```bash
   streamlit run app.py
   ```

3. 访问应用
   在浏览器中打开 http://localhost:8504（端口可能会有所不同）

## 测试

运行单元测试：

```bash
python -m pytest tests/ -v
```

验证 JSON 文件格式：

```bash
python validate_json.py
```

## 数据结构

### 知识图谱节点（graph_{course_id}.json）

```json
{
  "id": "node_001",
  "name": "货币的定义与职能",
  "prerequisites": [],
  "description": {
    "core_concept": "核心概念描述",
    "testable_angles": {
      "memory": "记忆层考察角度",
      "understanding": "理解层考察角度",
      "application": "应用层考察角度",
      "analysis": "分析层考察角度"
    },
    "confusable_points": "易混淆点描述"
  },
  "difficulty_coeff": 0.8
}
```

### 试题（questions_{course_id}.json）

```json
{
  "id": "q_001",
  "node_id": "node_001",
  "level": "understanding",
  "question": "题目内容",
  "options": ["A. 选项一", "B. 选项二", "C. 选项三", "D. 选项四"],
  "answer": "A",
  "explanation": "解析内容"
}
```

### 学生状态（student_{id}.json）

```json
{
  "student_id": "stu_001",
  "courses": {
    "course_finance_101": {
      "node_states": {
        "node_001": {
          "p_mastery": 0.62,
          "base_prob": 0.50,
          "difficulty_coeff": 0.80,
          "answered_count": 0,
          "last_updated": "2025-01-01T00:00:00"
        }
      },
      "answer_history": []
    },
    "course_linear_algebra": {
      "node_states": {
        "node_la_001": {
          "p_mastery": 0.5,
          "base_prob": 0.5,
          "difficulty_coeff": 0.7,
          "answered_count": 0,
          "last_updated": "2025-01-01T00:00:00"
        }
      },
      "answer_history": []
    }
  }
}
```

## 核心公式

### 初始掌握概率（二维加权平均）

```
初始概率 = 0.6 × 基础概率 + 0.4 × 难度系数

基础概率规则：
- 无先修节点：0.50
- 1个先修节点：0.35
- 2个先修节点：0.25
- 3个及以上先修节点：0.15
```

### BKT 贝叶斯更新

```
答对时：P_new = P(答对|已掌握) × P_old / P(答对)
答错时：P_new = P(答错|已掌握) × P_old / P(答错)

其中：
P(答对) = P(答对|已掌握) × P_old + P(答对|未掌握) × (1 - P_old)

默认参数：
- P(答对|已掌握) = 0.85（已掌握但答错的概率为0.15，即失误率）
- P(答对|未掌握) = 0.25（未掌握但猜对的概率，4选1）
```

### CAT 选题优先级

```
优先选择：图谱中"信息增益最大"的节点
具体规则：
1. 过滤掉已答题数 >= 3 的节点
2. 优先选择掌握概率接近 0.5 的节点（不确定性最高）
3. 在不确定性相近时，优先选先修节点覆盖更多后继的节点
```

## 界面说明

### 侧边栏
- 学生ID输入：用于标识学生身份
- 课程选择：可在"金融学基础"和"线性代数"之间切换
- 知识点掌握情况：显示每个知识点的掌握概率和进度条

### 主区域
- **自适应诊断**：显示当前题目，学生可以选择答案并提交，支持 LaTeX 数学公式渲染
- **知识图谱**：可视化展示知识点之间的关系和学生的掌握情况

## 注意事项

1. 项目使用 JSON 文件存储数据，不使用数据库
2. 学生状态文件存储在 `data/students/` 目录下，以学生ID命名
3. 知识图谱和题库需要手动编辑，确保数据格式正确
4. 数学公式使用 LaTeX 语法，需要正确转义反斜杠
5. 目前只支持单选题型

## 已实现的功能

1. ✅ 多课程支持（金融学基础和线性代数）
2. ✅ 独立的课程状态管理
3. ✅ LaTeX 数学公式渲染
4. ✅ 侧边栏显示/隐藏控制
5. ✅ 课程切换时内容自动更新

## 未来计划

1. 支持更多题型（多选题、简答题等）
2. 集成 LLM 生成题目和解析
3. 添加学习路径推荐功能
4. 优化知识图谱可视化效果
5. 支持更多课程的扩展

## 许可证

MIT License
