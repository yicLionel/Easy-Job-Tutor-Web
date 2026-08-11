# Easy Job Tutor · 公开 Beta

> 在线体验：https://easy-job-tutor-web.vercel.app/

Easy Job Tutor 面向在校大学生与应届毕业生，提供岗位 JD 关键词覆盖分析和简历原文证据辅助。当前 Beta 首版覆盖 AI 产品、AI Agent 开发与 AI 运营方向。

本工具不预测录用结果，也不代表招聘方或 ATS 评分。分析结果来自规则与关键词命中；用户必须核实每一项待确认事实，再将内容用于正式求职材料。

## 当前公开范围

| 模式 | 输入 | 输出 |
|------|------|------|
| 完整分析 | 岗位 JD + 简历 | 关键词覆盖、能力差距、简历原文证据和事实待确认提示 |
| 岗位拆解 | 仅岗位 JD | 职责、要求、工具、领域知识和软技能的关键词整理 |
| 简历诊断 | 仅简历 | 章节检测、原文亮点、问题和待补充信息 |

当前输出是求职材料整理辅助，不构成招聘建议或招聘决定，也不保证任何求职结果。

## 事实保护

- 关键词命中结果尽量关联到简历原文证据。
- 建议草稿中的新增数字、职责和成果必须标记为待确认。
- 用户需要确认所有待确认内容，确保最终材料准确且不具误导性。

## 隐私与处理方式

- PDF、DOCX 或 TXT 文件会发送到部署在 Vercel 的服务器函数，在该次请求中解析。
- 当前 Beta 不调用外部大型语言模型 API。
- 应用代码不会有意持久化保存原始文件或提取文本。
- 运营基础设施可能处理请求元数据；应用日志和分析排除文件名、JD、简历、原文证据、姓名、电子邮箱地址和电话号码。
- 请勿上传你无权处理的信息。完整说明见 [`privacy.html`](privacy.html)，使用规则见 [`terms.html`](terms.html)。

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | FastAPI（请求路由、文件解析与规则分析） |
| 前端 | Vue 3.5.18（同源静态运行时，无构建步骤） |
| 文件解析 | pdfplumber / pypdf / python-docx（PDF / DOCX / TXT） |
| 部署 | Vercel Serverless + 静态托管 |

## 目录结构

```text
.
├── index.html
├── app.js
├── styles.css
├── privacy.html
├── terms.html
├── vendor/
│   ├── vue.global.prod.js
│   └── VUE-LICENSE.txt
├── e2e/
├── tests/
└── api/
    ├── main.py
    ├── parser.py
    ├── matcher.py
    ├── learning.py
    └── knowledge.py
```

## 本地开发与测试

使用 Python 3.12 创建虚拟环境并安装开发依赖：

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r dev-requirements.txt
npm ci
npx playwright install chromium
```

运行静态检查、Python 测试和浏览器端到端测试：

```bash
npm run check
python -m unittest discover -s tests -v
npm run test:e2e
```

端到端测试会启动本地 FastAPI 服务，并覆盖桌面 Chromium 与 390px 宽移动视口。

## 联系

问题与隐私请求请提交到项目仓库的 [Issue 跟踪器](https://github.com/yicLionel/Easy-Job-Tutor-Web/issues)。
