# AI 简历优化助手 · 面试辅导 · 学习路线

面向**在校大学生 / 应届毕业生**的 AI 简历优化工具。首版聚焦三个岗位方向：**AI 产品 / AI Agent 开发 / AI 运营**。

产品采用**渐进式交互**：

1. **上传** — 粘贴岗位 JD + 上传简历（PDF / Word / TXT），选择目标岗位（或自动识别）
2. **匹配度分析** — SVG 分数环直观展示总匹配度 + 四个维度分（核心技能 / 项目经验 / 教育背景 / 综合素养）
3. **查漏补缺** — 按重要度排序的能力差距清单，每项附补齐建议与学习资源
4. **学习路线 & 面试辅导** — 分阶段学习路线 + 通用面试题 + 针对差距的追问，支持一键下载 Markdown 方案

## 技术栈

- 后端：**FastAPI**（简历解析、匹配度计算、学习路线生成）
- 前端：**Vue 3**（CDN，无构建步骤）
- 部署：**Vercel** Serverless（`api/index.py` + Mangum 适配）

## 目录结构

```
.
├── index.html            # 前端入口（Vercel 静态托管）
├── app.js                # Vue 3 前端逻辑
├── styles.css            # 样式
├── vercel.json           # Vercel 配置（仅 build env）
└── api/
    ├── index.py          # Vercel ASGI 入口（Mangum 包装 FastAPI）
    ├── main.py           # FastAPI 应用工厂
    ├── parser.py         # 简历文本抽取（PDF / Word / TXT）
    ├── matcher.py        # 匹配度评分
    ├── learning.py       # 学习路线 & 面试辅导生成
    ├── knowledge.py      # 三岗位技能知识库（核心配置）
    └── requirements.txt  # 部署依赖（含 mangum）
```

## 本地运行

依赖安装（使用虚拟环境）：

```bash
cd api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

打开 http://localhost:8000 即可使用。

> 也可以从项目根目录启动：`uvicorn api.main:app --port 8000`。

## 部署到 Vercel（公开）

本项目已改造为 Vercel 友好结构，两种方式任选：

### 方式 A：Vercel CLI

```bash
npm i -g vercel        # 或 npx vercel
vercel login
vercel                 # 首次部署（Framework 选 Other）
vercel --prod          # 推到生产，得到公开 *.vercel.app 域名
```

### 方式 B：连接 Git 仓库

1. 将本仓库推送到 GitHub / GitLab；
2. 打开 vercel.com → New Project → 导入仓库 → Framework Preset 选 **Other** → Deploy；
3. 部署完成后默认即为公开访问。

部署时 Vercel 会自动识别 `api/index.py` 为 Python 函数，并安装 `api/requirements.txt` 中的依赖，无需额外配置。

## 说明与后续

- 当前匹配度为**基于关键词命中的规则分析**（可解释、零成本、离线可用）。要升级为语义级评估，可接入大模型（Claude / OpenAI），替换 `backend/matcher.py` 内部实现即可，前端无需改动。
- 可扩展方向：简历扫描件 OCR、账号与历史记录、更多岗位模板、模拟面试对话。
