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
│   ├── graph_course_china_finance.json # 中国金融学知识图谱（从Excel导入）
│   ├── questions_course_china_finance.json # 中国金融学题库（66道）
│   ├── graph_course_philosophy.json    # 哲学通论知识图谱（从Excel导入，41个知识点，含modules）
│   ├── questions_course_philosophy.json # 哲学通论题库（123道，LLM生成）
│   ├── 中国金融学.xlsx                  # 原始知识图谱Excel数据
│   ├── 哲学通论.xlsx                    # 原始知识图谱Excel数据
│   └── students/                       # 学生状态文件
├── core/
│   ├── bkt.py                          # BKT 标准四参数模型更新逻辑
│   ├── cat.py                          # CAT 自适应选题逻辑（掌握阈值驱动）
│   ├── initializer.py                  # 初始概率计算
│   ├── llm_client.py                   # LLM API 调用封装
│   ├── survey.py                       # 入学问卷逻辑（模块自评 + 锚点测试）
│   └── learning_path.py                # 学习路径生成（拓扑排序 + 全图谱/指定目标）
├── utils/
│   └── io.py                           # JSON 读写工具
├── tests/
│   ├── test_bkt.py
│   ├── test_cat.py
│   ├── test_initializer.py
│   ├── test_survey.py                  # 问卷模块测试
│   └── test_learning_path.py           # 学习路径模块测试
├── docs/
│   ├── 算法说明_BKT与CAT.md            # BKT和CAT算法文档
│   ├── 算法说明_问卷与学习路径.md        # 问卷和学习路径算法文档
│   └── 新增学科操作指南.md              # 新增学科操作指南
├── app.py                              # Streamlit 主入口
├── requirements.txt                    # 依赖文件
├── .gitignore                         # Git 忽略文件
└── validate_json.py                    # JSON 验证工具
```

## 核心功能

1. **多课程支持**：支持金融学基础、线性代数、中国金融学和哲学通论四门课程，可在侧边栏自由切换
2. **独立的课程状态**：每个学生可以拥有多个课程的状态，切换课程时不会覆盖之前的状态
3. **入学问卷**：按模块粗粒度评估学生背景（4级自评），结合锚点测试验证高自评模块，精准调整初始掌握概率
4. **学习路径推荐**：基于知识图谱拓扑排序生成个性化学习路径，支持全图谱通关和指定目标模块两种模式
5. **学习路径可视化**：在知识图谱上以不同颜色和标记展示学习路径，当前节点红色高亮，已掌握绿色打勾，待学习橙色编号
6. **知识图谱可视化**：使用 pyvis 实现交互式知识图谱，展示知识点之间的先修关系和学生的掌握情况
7. **自适应诊断**：基于学生当前知识状态，自动选择信息增益最大的题目
8. **贝叶斯知识追踪**：标准四参数 BKT 模型，根据答题情况动态更新知识点掌握概率
9. **冷启动初始化**：基于知识图谱的先修关系和知识点难度，计算初始掌握概率
10. **实时反馈**：答题后立即显示答案解析和掌握概率变化
11. **LaTeX 数学公式渲染**：支持矩阵、行列式等数学公式的正确显示

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

### 学生状态（{student_id}.json）

```json
{
  "student_id": "stu_001",
  "courses": {
    "course_philosophy": {
      "node_states": {
        "node_phil_001": {
          "p_mastery": 0.62,
          "base_prob": 0.50,
          "difficulty_coeff": 0.80,
          "answered_count": 0,
          "last_updated": "2025-01-01T00:00:00"
        }
      },
      "answer_history": [],
      "survey_results": {
        "completed": true,
        "responses": {"mod_phil_01": 3, "mod_phil_02": 1},
        "anchor_tests": {"mod_phil_01": {"is_correct": true}}
      },
      "learning_path": {
        "mode": "full",
        "target_modules": [],
        "path_nodes": ["node_phil_001", "node_phil_004"],
        "current_index": 1
      }
    }
  }
}
```

## 核心公式

> 详细算法说明参见 [docs/算法说明_BKT与CAT.md](docs/算法说明_BKT与CAT.md)

### 初始掌握概率（二维加权平均）

```
初始概率 = 0.6 × 基础概率 + 0.4 × 难度系数

基础概率规则：
- 无先修节点：0.50
- 1个先修节点：0.35
- 2个先修节点：0.25
- 3个及以上先修节点：0.15
```

### BKT 标准四参数模型

```
四个参数：
- P(L₀)：初始掌握概率（由上述公式计算）
- P(T) = 0.10：学习转移概率（每次练习从未掌握转为掌握的概率）
- P(S) = 0.15：失误率（已掌握但答错的概率）
- P(G) = 0.25：猜测率（未掌握但答对的概率，4选1）

更新流程（每次答题后）：
1. 贝叶斯后验更新：根据答对/答错修正掌握概率
   答对时：P_posterior = P(correct|mastered) × P_old / P(correct)
   答错时：P_posterior = P(wrong|mastered) × P_old / P(wrong)

2. 学习转移：P_new = P_posterior + (1 - P_posterior) × P(T)
   练习本身带来学习效果，即使答错概率也不会断崖下跌

概率范围：[0.01, 1.0]，可自然趋近100%
```

### CAT 选题优先级

```
优先选择：图谱中"信息增益最大"的节点
具体规则：
1. 过滤掉已掌握（概率 >= 0.95）或无剩余题目的节点
2. 优先选择掌握概率接近 0.5 的节点（不确定性最高）
3. 在不确定性相近时，优先选先修节点覆盖更多后继的节点
4. 所有节点掌握或无题可出时，诊断结束
```

## 界面说明

### 侧边栏
- 学生ID输入：用于标识学生身份
- 课程选择：可在"金融学基础"、"线性代数"、"中国金融学"和"哲学通论"之间切换
- 重新做问卷：重置问卷和学习状态（仅在有 modules 的课程中显示）
- 知识点掌握情况：显示每个知识点的掌握概率和进度条

### 入学问卷（首次进入有 modules 的课程时自动触发）
- **自评阶段**：按模块显示4级熟悉度选项（没接触过/听说过/学过且有基础/掌握较好）
- **锚点测试**：对自评"学过"及以上的模块，出一道代表性题目验证，答错则下调该模块概率

### 主区域
- **自适应诊断**：CAT 选题，选择信息增益最大的知识点出题，支持 LaTeX 数学公式渲染
- **学习路径**：选择全图谱通关或指定目标模块，生成个性化学习路径，以知识图谱可视化方式展示路径进度，在路径中逐节点答题学习
- **知识图谱**：可视化展示知识点之间的关系和学生的掌握情况

## 注意事项

1. 项目使用 JSON 文件存储数据，不使用数据库
2. 学生状态文件存储在 `data/students/` 目录下，以学生ID命名
3. 知识图谱和题库需要手动编辑，确保数据格式正确
4. 数学公式使用 LaTeX 语法，需要正确转义反斜杠
5. 目前只支持单选题型

## 已实现的功能

1. ✅ 多课程支持（金融学基础、线性代数、中国金融学和哲学通论）
2. ✅ 独立的课程状态管理
3. ✅ LaTeX 数学公式渲染（题目、选项、解析均支持，使用 st.markdown 原生渲染）
4. ✅ 侧边栏显示/隐藏控制
5. ✅ 课程切换时内容自动更新
6. ✅ 从Excel知识图谱导入并生成图谱JSON（中国金融学，22个知识点，含前驱关系）
7. ✅ 从Excel知识图谱导入并生成图谱JSON（哲学通论，41个知识点，含前驱关系和模块分组）
8. ✅ 基于知识图谱节点生成多层级试题（memory/understanding/application，中国金融学66道，哲学通论123道）
9. ✅ 试题数据 LaTeX 公式规范化（修复转义问题，统一使用 $...$ 包裹数学表达式）
10. ✅ 通用化LLM试题生成脚本（支持命令行指定课程ID）
11. ✅ BKT 升级为标准四参数模型（加入学习转移概率 P(T)，掌握概率可自然趋近100%）
12. ✅ CAT 选题改为掌握阈值驱动（概率 >= 0.95 视为已掌握，替代固定答题次数上限）
13. ✅ 入学问卷系统（按模块粗粒度自评 + 锚点测试验证，精准调整初始概率）
14. ✅ 学习路径推荐（全图谱通关/指定目标模块两种模式，基于拓扑排序生成个性化路径）
15. ✅ 学习路径可视化（基于 pyvis 知识图谱展示路径，颜色区分当前/待学习/已掌握/非路径节点）
16. ✅ 学习路径答题流程（逐节点出题，掌握后自动前进，题目用完可重新练习或跳过）

## 未来计划

1. 支持更多题型（多选题、简答题等）
2. 集成 LLM 生成题目和解析
3. 添加学习路径推荐功能
4. 优化知识图谱可视化效果
5. 支持更多课程的扩展

## 许可证

MIT License
