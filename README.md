# AI 简历优化助手 · 面试辅导 · 学习路线

> **🌐 在线体验：https://easy-job-tutor-web.vercel.app/**

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

### JD 定制简历优化

- 从当前 JD 中筛选实际相关技能，再计算匹配度与能力差距
- 对简历中可识别的经历行生成**基于原文的 Bullet 改写草稿**
- 标出 JD 关键词、待补充关键词和需要用户确认的量化成果
- 展示原文 / 建议版本对比，并支持导出 Markdown 优化草稿
- 所有新增数字、职责和成果均标记为待确认，不自动编造候选人经历

### 查漏补缺 → 学习路线 → 面试辅导

- 按重要度排序的能力差距清单，每项附补齐建议与精选学习资源
- 分阶段学习路线（基础夯实 → 核心突破 → 高阶实战 → 作品集）
- 通用面试题 + 针对差距的定制追问
- 支持**一键下载**完整 Markdown 方案

### 简历 PDF 导出（前端生成）

- 结构化表单（基本信息 / 简介 / 教育 / 经历 / 项目 / 技能 / 荣誉）+ A4 实时预览
- 三种风格：**现代简约**（默认）、**经典专业**、**清爽创意**，风格来自 Easy-Job-Tutor Skill 的 PDF 设计规范
- **一键下载** A4 / Letter 简历 PDF，纯前端生成，**文字可选中、ATS 可读**，不依赖截图
- 中文使用子集化的思源黑体；导出时按需加载引擎与字体，不拖慢首屏
- 分析结果中的改写要点只取**简历原文**预填，`待确认` 内容不会被自动写入 PDF

### 其他

- 🌐 **中英文双语**：界面与分析结果一键切换（zh / en）
- 📱 响应式布局：桌面侧边栏 + 移动端抽屉导航
- 🔒 **隐私友好**：简历仅在应用内解析处理，无第三方上传、无外部 API 调用

---

## 🛠 技术栈

| 层 | 技术 |
|----|------|
| 后端 | **FastAPI**（简历解析、匹配度计算、路线生成） |
| 前端 | **Vue 3**（CDN 引入，无框架构建步骤） |
| PDF 导出 | **@hmfw/html-to-pdf**（pdf-lib，矢量文字）+ esbuild 打包，字体子集化 |
| 简历解析 | pdfplumber / pypdf / python-docx（PDF / Word / TXT） |
| 部署 | **Vercel** Serverless + 静态托管 |

---

## 📁 目录结构

```
.
├── index.html            # 前端入口（Vercel 静态托管）
├── app.js                # Vue 3 前端逻辑
├── styles.css            # 样式
├── vendor/               # 浏览器 PDF 引擎产物（构建生成）
├── fonts/                # 子集化中文预览字体 + @font-face
├── build/                # 打包、字体子集化与验证脚本
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

## ✅ 测试

```bash
pytest tests/
```

覆盖：API 入口点可用性、简历文本解析（PDF / Word / TXT）、JD 定向匹配和事实保护型优化草稿。

### PDF 导出构建与验证

`vendor/` 与 `fonts/` 已随仓库提供，常规开发无需重新构建；修改依赖或字体时才需要：

```bash
npm install              # 安装 esbuild / @hmfw/html-to-pdf
npm run build:pdf        # 重新打包 vendor/html-to-pdf.browser.js
npm run build:fonts      # 从 fonts/raw-*.woff 重新生成子集字体
npm run check            # JS 语法检查
npm run verify:pdf       # 无头浏览器导出 PDF 并校验中文可选中
npm run verify:app       # 驱动真实页面走完分析 → 导出流程（需先启动服务）
```

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
