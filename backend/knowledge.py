# -*- coding: utf-8 -*-
"""
三岗位知识库：技能图谱、匹配关键词、学习资源与面试问题。

维度说明：
- 核心技能：岗位硬技能
- 项目经验：是否有相关落地 / 项目经历
- 教育背景：专业 / 学历相关性
- 综合素养：软技能

importance: 1(锦上添花) ~ 5(必备)。匹配度按权重汇总；差距按 importance 排序。
"""

DIMENSIONS = ["核心技能", "项目经验", "教育背景", "综合素养"]

# 通用学习资源兜底
GENERIC_RESOURCE = {"name": "在 B 站 / 掘金搜索对应关键词", "url": "https://search.bilibili.com/all?keyword="}

ROLES = {
    "ai_product": {
        "label": "AI 产品",
        "desc": "面向 AI 产品的需求洞察、LLM 应用认知与 0-1 落地能力。",
        "skills": [
            # 核心技能
            {"id": "ap_req", "label": "需求分析", "dim": "核心技能", "importance": 5,
             "keywords": ["需求分析", "需求调研", "requirement", "用户痛点", "场景梳理"],
             "learn": "练习把模糊诉求拆成可验证的用户故事与验收标准，建立 MRD/PRD 思维。",
             "resource": {"name": "《启示录》+ 人人都是产品经理", "url": "https://www.woshipm.com"}},
            {"id": "ap_user", "label": "用户研究", "dim": "核心技能", "importance": 4,
             "keywords": ["用户研究", "用户访谈", "user research", "调研", "用户画像", "问卷"],
             "learn": "掌握访谈提纲设计、定性+定量结合的研究方法，建立用户同理心。",
             "resource": {"name": " Nielsen Norman Group", "url": "https://www.nngroup.com"}},
            {"id": "ap_prd", "label": "PRD 撰写", "dim": "核心技能", "importance": 4,
             "keywords": ["prd", "产品需求文档", "需求文档", "产品文档"],
             "learn": "用结构化模板写 PRD：背景、目标、范围、功能列表、交互、数据埋点。",
             "resource": {"name": "腾讯 CDC PRD 模板", "url": "https://cdc.tencent.com"}},
            {"id": "ap_proto", "label": "产品原型", "dim": "核心技能", "importance": 3,
             "keywords": ["原型", "axure", "figma", "墨刀", "线框图", "wireframe", "交互设计"],
             "learn": "熟练 Figma 画出可点击原型，能和技术对齐交互细节。",
             "resource": {"name": "Figma 官方教程", "url": "https://www.figma.com/resources/learn-design/"}},
            {"id": "ap_data", "label": "数据分析", "dim": "核心技能", "importance": 4,
             "keywords": ["数据分析", "data analysis", "埋点", "指标", "ab测试", "a/b", "留存", "转化"],
             "learn": "会用 SQL/神策/GA 看核心指标，用数据驱动迭代决策。",
             "resource": {"name": "SQL 菜鸟教程", "url": "https://www.runoob.com/sql/sql-tutorial.html"}},
            {"id": "ap_ab", "label": "A/B 测试", "dim": "核心技能", "importance": 2,
             "keywords": ["a/b", "ab测试", "ab experiment", "灰度", "实验"],
             "learn": "理解实验设计的基本统计原理（显著性、样本量）。",
             "resource": {"name": "Evan Miller 在线工具", "url": "https://www.evanmiller.org/ab-testing/"}},
            {"id": "ap_comp", "label": "竞品分析", "dim": "核心技能", "importance": 3,
             "keywords": ["竞品", "competitive", "对标", "benchmark"],
             "learn": "建立竞品矩阵分析法（功能/体验/商业模式三维度）。",
             "resource": {"name": "在 36氪 / 晚点搜索赛道", "url": "https://36kr.com"}},
            {"id": "ap_ml", "label": "机器学习基础", "dim": "核心技能", "importance": 3,
             "keywords": ["机器学习", "深度学习", "ml", "神经网络", "模型", "算法"],
             "learn": "理解监督/无监督、训练/推理、常见模型能力边界，能和算法同学对话。",
             "resource": {"name": "吴恩达 ML 专项", "url": "https://www.coursera.org/specializations/machine-learning-introduction"}},
            {"id": "ap_llm", "label": "LLM 应用认知", "dim": "核心技能", "importance": 5,
             "keywords": ["大模型", "llm", "gpt", "大语言模型", "aigc", "生成式", "prompt", "提示词"],
             "learn": "亲自用过主流大模型与 Agent 产品，理解 RAG/Agent/微调的适用边界与产品形态。",
             "resource": {"name": "OpenAI 官方 Cookbook", "url": "https://cookbook.openai.com"}},
            {"id": "ap_biz", "label": "商业化思维", "dim": "核心技能", "importance": 3,
             "keywords": ["商业化", "变现", "营收", "商业", "收费", "订阅", "定价"],
             "learn": "能设计定价/增长模型，理解 PMF 与单位经济。",
             "resource": {"name": "《增长黑客》", "url": "https://book.douban.com"}},

            # 项目经验
            {"id": "ap_01", "label": "0-1 产品经验", "dim": "项目经验", "importance": 4,
             "keywords": ["从0到1", "0到1", "0-1", "孵化", "mvp", "立项", "搭建产品"],
             "learn": "争取独立负责一个小功能或副业项目的从 0 到 1，沉淀复盘文档。",
             "resource": {"name": "做 1 个 AI 小工具并上线", "url": "https://vercel.com"}},
            {"id": "ap_ship", "label": "AI 产品落地", "dim": "项目经验", "importance": 4,
             "keywords": ["落地", "上线", "交付", "发布", "迭代", "上线运营"],
             "learn": "跑通过需求→开发→灰度→上线的完整闭环，准备项目复盘稿。",
             "resource": GENERIC_RESOURCE},
            {"id": "ap_cross", "label": "跨团队协作", "dim": "项目经验", "importance": 3,
             "keywords": ["跨团队", "协作", "协调", "推动", "对齐", "项目管理"],
             "learn": "练习用 OKR/周会机制推动设计、研发、算法协同。",
             "resource": GENERIC_RESOURCE},
            {"id": "ap_pm", "label": "项目管理", "dim": "项目经验", "importance": 3,
             "keywords": ["项目管理", "pmp", "排期", "迭代", "敏捷", "scrum"],
             "learn": "掌握看板/里程碑管理，能控进度与风险。",
             "resource": {"name": " Atlassian 项目管理指南", "url": "https://www.atlassian.com/agile"}},

            # 教育背景
            {"id": "ap_edu", "label": "计算机/相关专业", "dim": "教育背景", "importance": 2,
             "keywords": ["计算机", "软件", "信息", "数据科学", "人工智能", "产品", "统计", "数学"],
             "learn": "若非相关背景，可补 1 门产品/数据分析入门课增强说服力。",
             "resource": GENERIC_RESOURCE},
            {"id": "ap_deg", "label": "学历背景", "dim": "教育背景", "importance": 1,
             "keywords": ["本科", "硕士", "博士", "bachelor", "master", "985", "211"],
             "learn": "学历为加分项，重点仍应放在项目与作品集。",
             "resource": GENERIC_RESOURCE},

            # 综合素养
            {"id": "ap_comm", "label": "沟通表达", "dim": "综合素养", "importance": 3,
             "keywords": ["沟通", "表达", "汇报", "演讲", "ppt", "presentation"],
             "learn": "练习结构化表达（结论先行），沉淀 1 份产品汇报 PPT。",
             "resource": GENERIC_RESOURCE},
            {"id": "ap_logic", "label": "逻辑思维", "dim": "综合素养", "importance": 3,
             "keywords": ["逻辑", "结构化", "复盘", "分析"],
             "learn": "用 MECE / 金字塔原理组织分析与汇报。",
             "resource": {"name": "《金字塔原理》", "url": "https://book.douban.com"}},
            {"id": "ap_learn", "label": "快速学习", "dim": "综合素养", "importance": 2,
             "keywords": ["自学", "快速学习", "自我驱动", "学习能力强"],
             "learn": "建立知识管理习惯（笔记/卡片盒），持续追踪 AI 新动态。",
             "resource": GENERIC_RESOURCE},
        ],
        "interview_base": [
            "请用 3 分钟介绍你最满意的一个产品项目，以及你在其中承担的角色。",
            "如果让你从 0 到 1 设计一款面向大学生的 AI 学习助手，你会怎么切入？",
            "你如何判断一个 AI 功能该用 RAG 还是微调？请结合产品目标说明。",
            "请举一个你用数据驱动产品迭代的例子。",
        ],
    },

    "ai_agent": {
        "label": "AI Agent 开发",
        "desc": "面向 LLM / Agent 的工程实现能力：RAG、MCP、多智能体与工程落地。",
        "skills": [
            # 核心技能
            {"id": "aa_py", "label": "Python", "dim": "核心技能", "importance": 5,
             "keywords": ["python", "py", "pandas", "numpy"],
             "learn": "扎实的 Python 基础（异步、类型注解、虚拟环境、包管理）。",
             "resource": {"name": "Python 官方教程", "url": "https://docs.python.org/zh-cn/3/tutorial/"}},
            {"id": "aa_js", "label": "前端/TS 基础", "dim": "核心技能", "importance": 2,
             "keywords": ["javascript", "typescript", "js", "ts", "node", "前端"],
             "learn": "能用 TS 写简单前端或后端，便于做 Agent 的可视化与联调。",
             "resource": {"name": "TypeScript 官方手册", "url": "https://www.typescriptlang.org/docs/"}},
            {"id": "aa_lc", "label": "LangChain/LangGraph", "dim": "核心技能", "importance": 4,
             "keywords": ["langchain", "langgraph", "langchain.js"],
             "learn": "用 LangGraph 编排有状态的多步 Agent 工作流。",
             "resource": {"name": "LangChain 文档", "url": "https://python.langchain.com/docs/introduction/"}},
            {"id": "aa_rag", "label": "RAG 检索增强", "dim": "核心技能", "importance": 5,
             "keywords": ["rag", "检索增强", "向量检索", "知识库问答", "embedding"],
             "learn": "掌握切分/向量化/重排/引用溯源的完整 RAG 链路与评测。",
             "resource": {"name": "LangChain RAG 教程", "url": "https://python.langchain.com/docs/tutorials/rag/"}},
            {"id": "aa_mcp", "label": "MCP 协议", "dim": "核心技能", "importance": 4,
             "keywords": ["mcp", "model context protocol", "工具调用", "function calling"],
             "learn": "理解 MCP 客户端/服务端模型，能为 Agent 封装工具服务。",
             "resource": {"name": "MCP 官方规范", "url": "https://modelcontextprotocol.io"}},
            {"id": "aa_api", "label": "大模型 API", "dim": "核心技能", "importance": 5,
             "keywords": ["claude api", "openai api", "gpt api", "大模型api", "api调用", "anthropic", "智谱", "通义", "kimi"],
             "learn": "熟练调用主流大模型 API，掌握流式输出、重试、降级与成本控制。",
             "resource": {"name": "OpenAI API 文档", "url": "https://platform.openai.com/docs"}},
            {"id": "aa_vec", "label": "向量数据库", "dim": "核心技能", "importance": 4,
             "keywords": ["向量数据库", "vector", "faiss", "milvus", "chroma", "pgvector", "qdrant"],
             "learn": "选型并落地一种向量库，理解索引与相似度度量。",
             "resource": {"name": "Chroma 文档", "url": "https://docs.trychroma.com"}},
            {"id": "aa_prompt", "label": "提示工程", "dim": "核心技能", "importance": 4,
             "keywords": ["提示工程", "prompt", "提示词", "few-shot", "chain-of-thought", "cot"],
             "learn": "掌握角色/约束/示例/思维链等提示技巧与系统提示设计。",
             "resource": {"name": "Prompt Engineering Guide", "url": "https://www.promptingguide.ai/zh"}},
            {"id": "aa_agent", "label": "Agent 架构", "dim": "核心技能", "importance": 5,
             "keywords": ["agent", "智能体", "多智能体", "multi-agent", "自主", "规划", "反思"],
             "learn": "理解规划-执行-反思循环，能设计单/多 Agent 协作架构。",
             "resource": {"name": "AutoGen 文档", "url": "https://microsoft.github.io/autogen/"}},
            {"id": "aa_backend", "label": "后端开发", "dim": "核心技能", "importance": 4,
             "keywords": ["后端", "fastapi", "flask", "django", "微服务", "api", "restful"],
             "learn": "用 FastAPI 构建稳定的 Agent 服务与 API。",
             "resource": {"name": "FastAPI 文档", "url": "https://fastapi.tiangolo.com/zh/"}},
            {"id": "aa_fe", "label": "前端基础", "dim": "核心技能", "importance": 2,
             "keywords": ["前端", "vue", "react", "html", "css"],
             "learn": "能用 Vue/React 做简单交互页，便于联调 Agent 界面。",
             "resource": {"name": "Vue 官方教程", "url": "https://cn.vuejs.org/guide/introduction.html"}},
            {"id": "aa_ft", "label": "模型微调", "dim": "核心技能", "importance": 3,
             "keywords": ["微调", "fine-tune", "finetuning", "lora", "sft", "peft"],
             "learn": "理解 SFT/LoRA 流程与适用场景，知道何时该微调而非提示。",
             "resource": {"name": "HuggingFace PEFT", "url": "https://huggingface.co/docs/peft"}},
            {"id": "aa_deploy", "label": "部署/推理优化", "dim": "核心技能", "importance": 3,
             "keywords": ["部署", "docker", "k8s", "推理", "inference", "性能优化", "量化", "vllm"],
             "learn": "会用 Docker 部署服务，了解推理加速与成本优化。",
             "resource": {"name": "Docker 官方教程", "url": "https://docs.docker.com/get-started/"}},

            # 项目经验
            {"id": "aa_proj", "label": "Agent 项目经验", "dim": "项目经验", "importance": 5,
             "keywords": ["agent项目", "智能体项目", "搭建agent", "agent开发", "rag系统", "对话系统"],
             "learn": "做一个端到端 Agent（如简历优化/客服/数据分析），写清架构与难点。",
             "resource": {"name": "在 GitHub 开源你的 Agent", "url": "https://github.com"}},
            {"id": "aa_full", "label": "全栈交付", "dim": "项目经验", "importance": 4,
             "keywords": ["全栈", "端到端", "完整项目", "前后端", "独立开发"],
             "learn": "独立完成从需求到上线的完整链路，沉淀可演示 Demo。",
             "resource": GENERIC_RESOURCE},
            {"id": "aa_oss", "label": "开源贡献", "dim": "项目经验", "importance": 2,
             "keywords": ["开源", "github", "贡献", "pr", "开源项目"],
             "learn": "给 1-2 个 AI 开源项目提 PR，体现工程协作能力。",
             "resource": {"name": "GitHub Trending", "url": "https://github.com/trending"}},

            # 教育背景
            {"id": "aa_edu", "label": "计算机/AI 相关", "dim": "教育背景", "importance": 3,
             "keywords": ["计算机", "软件", "人工智能", "数据科学", "自动化", "电子信息", "统计"],
             "learn": "若非相关背景，可用项目作品集弥补专业相关性。",
             "resource": GENERIC_RESOURCE},
            {"id": "aa_algo", "label": "算法基础", "dim": "教育背景", "importance": 3,
             "keywords": ["算法", "数据结构", "leetcode", "刷题"],
             "learn": "刷透常见数据结构与算法，应对技术面试笔试。",
             "resource": {"name": "LeetCode", "url": "https://leetcode.cn"}},

            # 综合素养
            {"id": "aa_git", "label": "工程规范", "dim": "综合素养", "importance": 3,
             "keywords": ["git", "测试", "文档", "代码规范", "ci", "单元测试"],
             "learn": "养成写测试、写 README、用 Git 协作的工程师习惯。",
             "resource": {"name": "Pro Git 中文", "url": "https://git-scm.com/book/zh/v2"}},
            {"id": "aa_debug", "label": "问题排查", "dim": "综合素养", "importance": 3,
             "keywords": ["调试", "排障", "排查", "定位", "日志", "监控"],
             "learn": "建立日志/可观测性意识，能系统性定位线上问题。",
             "resource": GENERIC_RESOURCE},
        ],
        "interview_base": [
            "请讲一个你做过的 Agent / RAG 项目，技术栈、架构和你踩过的坑。",
            "如何为 Agent 设计一个带工具调用与失败重试的循环？",
            "RAG 效果不好时，你会从哪些环节排查并优化？",
            "如果大模型 API 超时或幻觉，你的系统如何降级保证体验？",
        ],
    },

    "ai_ops": {
        "label": "AI 运营",
        "desc": "用 AI 工具提效的内容、用户增长与社群运营能力。",
        "skills": [
            # 核心技能
            {"id": "ao_content", "label": "内容运营", "dim": "核心技能", "importance": 5,
             "keywords": ["内容运营", "内容策划", "文案", "新媒体", "选题", "创作", "公众号", "小红书"],
             "learn": "建立选题-创作-分发-复盘的内容闭环，沉淀爆款方法论。",
             "resource": {"name": "新榜 / 小红书创作学院", "url": "https://www.newrank.cn"}},
            {"id": "ao_growth", "label": "用户增长", "dim": "核心技能", "importance": 4,
             "keywords": ["用户增长", "增长", "拉新", "留存", "转化", "裂变"],
             "learn": "理解 AARRR 漏斗，能用活动/渠道驱动增长。",
             "resource": {"name": "《增长黑客》", "url": "https://book.douban.com"}},
            {"id": "ao_comm", "label": "社群/私域运营", "dim": "核心技能", "importance": 4,
             "keywords": ["社群", "社区", "私域", "用户运营", "会员", "活跃"],
             "learn": "搭建社群 SOP（拉新-促活-转化），提升留存与活跃。",
             "resource": {"name": "企业微信运营中心", "url": "https://work.weixin.qq.com"}},
            {"id": "ao_data", "label": "数据分析", "dim": "核心技能", "importance": 4,
             "keywords": ["数据分析", "数据看板", "指标", "gmv", "roi", "转化", "留存"],
             "learn": "会用飞书多维表格/BI 看板追踪核心运营指标。",
             "resource": {"name": "飞书多维表格", "url": "https://www.feishu.cn/product/base"}},
            {"id": "ao_act", "label": "活动策划", "dim": "核心技能", "importance": 3,
             "keywords": ["活动策划", "运营活动", "营销活动", "策划", "执行"],
             "learn": "能从目标拆活动方案，控预算与节奏并做复盘。",
             "resource": GENERIC_RESOURCE},
            {"id": "ao_aitool", "label": "AI 工具应用", "dim": "核心技能", "importance": 5,
             "keywords": ["ai工具", "chatgpt", "copilot", "效率工具", "aigc", "文心", "豆包", "kimi", "智能体"],
             "learn": "把 AI 用于选题、脚本、图文批量生产，沉淀自己的工作流。",
             "resource": {"name": "AI 工具导航", "url": "https://www.aicollection.com"}},
            {"id": "ao_prompt", "label": "Prompt 工程", "dim": "核心技能", "importance": 3,
             "keywords": ["提示词", "prompt", "提示工程", "ai 写作"],
             "learn": "用结构化提示批量产出稳定质量的运营内容。",
             "resource": {"name": " Prompt 工程指南", "url": "https://www.promptingguide.ai/zh"}},
            {"id": "ao_auto", "label": "自动化工作流", "dim": "核心技能", "importance": 3,
             "keywords": ["自动化", "工作流", "n8n", "zapier", "飞书机器人", "脚本", "批量"],
             "learn": "用 n8n/飞书机器人把重复运营动作自动化。",
             "resource": {"name": "n8n 官方文档", "url": "https://docs.n8n.io"}},
            {"id": "ao_channel", "label": "渠道投放", "dim": "核心技能", "importance": 3,
             "keywords": ["投放", "广告", "渠道", "sem", "信息流", "买量"],
             "learn": "理解主流投放渠道与 ROI 核算，能小预算跑通测试。",
             "resource": GENERIC_RESOURCE},
            {"id": "ao_user", "label": "用户研究", "dim": "核心技能", "importance": 3,
             "keywords": ["用户调研", "用户画像", "访谈", "问卷", "痛点"],
             "learn": "建立用户画像与需求分层，指导内容与活动。",
             "resource": GENERIC_RESOURCE},

            # 项目经验
            {"id": "ao_01", "label": "0-1 运营经验", "dim": "项目经验", "importance": 4,
             "keywords": ["从0到1", "0到1", "冷启动", "搭建", "从零", "起号"],
             "learn": "独立操盘一个账号/社群的冷启动，沉淀增长复盘。",
             "resource": GENERIC_RESOURCE},
            {"id": "ao_ship", "label": "活动落地", "dim": "项目经验", "importance": 4,
             "keywords": ["活动执行", "落地", "复盘", "操盘", "上线"],
             "learn": "完整跑过一次活动（策划-执行-数据-复盘）。",
             "resource": GENERIC_RESOURCE},
            {"id": "ao_prod", "label": "内容生产", "dim": "项目经验", "importance": 4,
             "keywords": ["内容生产", "选题", "创作", "脚本", "图文", "短视频"],
             "learn": "产出可量化的内容成果（阅读/涨粉/转化），备好作品集。",
             "resource": GENERIC_RESOURCE},

            # 教育背景
            {"id": "ao_edu", "label": "市场/传媒/商科相关", "dim": "教育背景", "importance": 2,
             "keywords": ["市场营销", "传媒", "新闻", "工商管理", "运营", "广告", "传播"],
             "learn": "若非相关背景，可用运营作品集证明能力。",
             "resource": GENERIC_RESOURCE},
            {"id": "ao_dataedu", "label": "数据/商科", "dim": "教育背景", "importance": 2,
             "keywords": ["数据", "商科", "经济", "统计", "管理"],
             "learn": "补一点数据分析基础，对运营量化很有帮助。",
             "resource": {"name": "可汗学院统计学", "url": "https://zh.khanacademy.org/math/statistics-probability"}},

            # 综合素养
            {"id": "ao_copy", "label": "文案写作", "dim": "综合素养", "importance": 4,
             "keywords": ["写作", "文案", "公众号", "小红书", "标题", "脚本"],
             "learn": "练习不同平台的文案风格，建立标题与钩子方法论。",
             "resource": GENERIC_RESOURCE},
            {"id": "ao_exec", "label": "沟通协调", "dim": "综合素养", "importance": 3,
             "keywords": ["沟通", "协调", "执行", "推进", "跨部门"],
             "learn": "强执行力+跨团队推进，是运营岗的核心软素质。",
             "resource": GENERIC_RESOURCE},
        ],
        "interview_base": [
            "请分享一个你从 0 到 1 做起来的账号/社群/活动，关键动作和数据结果是什么？",
            "你如何用 AI 工具把日常运营效率提升一倍？请给具体例子。",
            "如果活动转化不达标，你会从哪些环节做复盘和优化？",
            "请现场为一款 AI 产品写一条面向大学生的小红书推广文案。",
        ],
    },
}


def auto_detect_role(text: str) -> str:
    """根据 JD 文本粗略判断最匹配的岗位。"""
    t = (text or "").lower()
    scores = {}
    for rid, spec in ROLES.items():
        s = 0
        for sk in spec["skills"]:
            s += sum(1 for k in sk["keywords"] if k.lower() in t)
        scores[rid] = s
    best = max(scores, key=scores.get)
    # 若完全无命中，回退到 ai_product
    return best if scores[best] > 0 else "ai_product"
