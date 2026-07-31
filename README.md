# AI 简历优化助手 · 面试辅导 · 学习路线

> An AI-powered resume analyzer built for students and fresh graduates targeting AI-related roles.
> Paste a job description, upload your resume, and get an explainable match analysis, gap list, learning path, and interview prep — for free, with zero API cost.

面向**在校大学生 / 应届毕业生**的 AI 简历优化工具，覆盖三大热门岗位方向：**AI 产品经理 / AI Agent 开发 / AI 运营**（可自动识别岗位方向）。

产品的核心是**可解释**：每一步结论都基于规则与关键词命中，能从简历原文追溯到证据，无任何大模型 API 调用——零成本、离线可用、隐私友好。

---

## ✨ 功能特性

### 四种分析模式（自动路由，也可手动指定）

| 模式 | 输入 | 输出 |
|------|------|------|
| **全链路分析** | 岗位 JD + 简历 | 匹配度总评、四维分、五维评审、事实台账、差距清单、学习路线、面试题 |
| **岗位拆解** | 仅岗位 JD | 必需技能 / 加分技能 / 工具技术 / 领域知识 / 软技能 / 隐性要求 |
| **简历诊断** | 仅简历 | 章节完整度、亮点、问题、针对性追问 |
| **多岗位对比** | 多个 JD + 简历 | 横向评分对比、共同优势、岗位间差异点 |

### 匹配分析（全链路模式）

- **总分 + 四维分**：核心技能 / 项目经验 / 教育背景 / 综合素养，SVG 分数环直观展示（0–100，随分数变色）
- **五维评审**：岗位匹配度、ATS 系统友好度、HR 扫描体验、面试准备度、简历可信度，每项附证据与改进建议
- **事实台账**：逐项列出命中的技能，标注重要度（P1–P5）与**简历原文证据**，匹配结果可追溯

### 查漏补缺 → 学习路线 → 面试辅导

- 按重要度排序的能力差距清单，每项附补齐建议与精选学习资源
- 分阶段学习路线（基础夯实 → 核心突破 → 高阶实战 → 作品集）
- 通用面试题 + 针对差距的定制追问
- 支持**一键下载**完整 Markdown 方案

### 其他

- 🌐 **中英文双语**：界面与分析结果一键切换（zh / en）
- 📱 响应式布局：桌面侧边栏 + 移动端抽屉导航
- 🔒 **隐私友好**：简历仅在应用内解析处理，无第三方上传、无外部 API 调用

---

## 🛠 技术栈

| 层 | 技术 |
|----|------|
| 后端 | **FastAPI**（简历解析、匹配度计算、路线生成） |
| 前端 | **Vue 3**（CDN 引入，无构建步骤） |
| 简历解析 | pdfplumber / pypdf / python-docx（PDF / Word / TXT） |
| 部署 | **Vercel** Serverless + 静态托管 |

---

## 📁 目录结构

```
.
├── index.html            # 前端入口（Vercel 静态托管）
├── app.js                # Vue 3 前端逻辑
├── styles.css            # 样式
├── requirements.txt      # Python 依赖（Vercel 从项目根目录读取）
├── .python-version       # Vercel Python 版本
├── vercel.json           # Vercel 配置（零配置路由）
├── tests/                # 单元测试（入口点 / 简历解析）
└── api/
    ├── index.py          # Vercel ASGI 入口
    ├── health.py         # Vercel 入口 → /api/health
    ├── analyze.py        # Vercel 入口 → /api/analyze
    ├── main.py           # FastAPI 应用工厂（模式路由 Gate 系统）
    ├── parser.py         # 简历文本抽取（PDF / Word / TXT）
    ├── matcher.py        # 匹配度评分、五维评审、事实台账、多 JD 对比
    ├── learning.py       # 学习路线 & 面试辅导生成
    └── knowledge.py      # 三岗位技能知识库（核心配置，中英双语关键词）
```

---

## 🚀 本地运行

```bash
# 1. 创建并激活虚拟环境
python -m venv .venv && source .venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
uvicorn api.main:app --reload --port 8000
```

打开 http://localhost:8000 即可使用（本地由 FastAPI 直接托管前端）。

---

## ☁️ 部署到 Vercel

本项目为 Vercel 友好结构，两种方式任选：

**方式 A：Vercel CLI**

```bash
npm i -g vercel        # 或 npx vercel
vercel login
vercel                 # 首次部署（Framework 选 Other）
vercel --prod          # 推送到生产，得到公开 *.vercel.app 域名
```

**方式 B：连接 Git 仓库**

1. 将本仓库推送到 GitHub / GitLab；
2. 打开 vercel.com → New Project → 导入仓库 → Framework Preset 选 **Other** → Deploy；
3. 部署完成后默认公开访问。

部署时 Vercel 会安装根目录 `requirements.txt` 的依赖；`api/health.py`、`api/analyze.py`、`api/index.py` 为对应 URL 提供函数入口，复用同一个 FastAPI 应用，无需 rewrite。

---

## ✅ 测试

```bash
pytest tests/
```

覆盖：API 入口点可用性、简历文本解析（PDF / Word / TXT）。

---

## 🗺 后续规划

- [ ] 简历扫描件 OCR 识别
- [ ] 账号体系与历史记录
- [ ] 更多岗位模板（产品、算法、研发、运营等）
- [ ] 语义级匹配（可选接入大模型，替换 `api/matcher.py` 内部实现即可，前端无需改动）
- [ ] 模拟面试对话

---

## 📄 说明

- 当前匹配度为**基于关键词命中的规则分析**（可解释、零成本、离线可用），非语义评估。
- 若需语义级评估，可接入 Claude / OpenAI 等大模型，只需替换 `api/matcher.py` 内部实现。
- 支持中英文 JD 与简历（知识库内置双语关键词）。
