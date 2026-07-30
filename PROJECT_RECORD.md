# 项目记录：AI 简历优化助手 · 面试辅导 · 学习路线

> 项目代号：Easy-Job-Tutor-Web
> 仓库地址：https://github.com/yicLionel/Easy-Job-Tutor-Web

---

## 一、项目概述

面向**在校大学生 / 应届毕业生**的 AI 简历优化工具，首版覆盖三个热门岗位方向：**AI 产品经理 / AI Agent 开发 / AI 运营**。

产品采用**渐进式四步交互**：

| 步骤 | 功能 | 用户操作 |
|------|------|----------|
| ① | **上传** | 粘贴岗位 JD + 上传简历（PDF / Word / TXT），选择目标岗位或自动识别 |
| ② | **匹配度分析** | SVG 分数环（0–100，变色）+ 四个维度分（核心技能 / 项目经验 / 教育背景 / 综合素养）+ 已命中能力列表 |
| ③ | **查漏补缺** | 按重要度（P5~P1）排序的差距清单，每项附补齐建议与学习资源链接 |
| ④ | **学习���线 & 面试辅导** | 分四阶段学习路线（基础夯实 → 核心突破 → 高阶实战 → 作品集）+ 通用面试题 + 针对差距的追问，支持一键下载 Markdown 方案 |

## 二、技术栈

| 层 | 技术 | 说明 |
|----|------|------|
| 后端框架 | **FastAPI** (Python) | RESTful API，简历解析 / 匹配度计算 / 学习路线生成 |
| 前端 | **Vue 3** (CDN) | 无构建步骤，单 HTML 文件引入 |
| 样式 | **CSS** (自定义) | 无框架依赖 |
| 本��开发 | **uvicorn** | `uvicorn api.main:app --port 8000` |
| 线上部署 | **Vercel** | Serverless 函数 + 静态托管 |
| 版本控制 | **Git + GitHub** | 公开仓库 |

## 三、架构

```
├── index.html            # 前端入口（Vercel 托管静态）
├── app.js                # Vue 3 前端逻辑
├── styles.css            # 样式
├── vercel.json           # Vercel 部署配置
├── README.md             # 使用说明
├── .gitignore            # Git 忽略规则
└── api/                  # 后端（所有代码在同一目录，Vercel 自动打包）
    ├── index.py          # Vercel 入口（导出 FastAPI app 变量）
    ├── main.py           # FastAPI 应用工厂（路由 / 逻辑编排）
    ├── parser.py         # 简历文本抽取（PDF / Word / TXT，重依赖延迟导入）
    ├── matcher.py        # 匹配度评分（规则引擎：关键词命中 + 重要性加权）
    ├── learning.py       # 学习路线 & 面试辅导生成
    ├── knowledge.py      # 三岗位技能知识库（核心配置：技能图谱 / 关键词 / 权重 / 资源）
    └── requirements.txt  # Python 依赖
```

### 匹配算法逻辑

1. 根据 JD 文本中的关键词自动识别目标岗位（三层权重：高权词直接判定 → ���权词计数 → 低权词加权）
2. 按 4 个维度（核心技能 / 项目经验 / 教育背景 / 综合素养）扫描简历
3. 每个技能 = 关键词命中次数 × 重要性权重 → 汇总为维度分 → 归一化为总分
4. 完全未命中的技能 → 输出差距清单（按重要度排序）

### 核心数据流

```
用户上传 (JD + 简历 PDF/Word/TXT)
  → parser.py 提取纯文本
  ��� matcher.py 岗位识别 + 匹配度评分 + 差距检测
  → learning.py 生成学习路线 + 面试辅导
  → 前端���染分数环、差距列表、路线与面试题
```

## 四、开发历程

### 初始化阶段

1. 搭建项目骨架（平行 backend/ + frontend/ 目录）
2. 实现三岗位知识库（`knowledge.py`）：AI 产品 / AI Agent 开发 / AI 运营，每岗位 15–20 项技能
3. 实现简历解析（`parser.py`）：PDF 用 pdfplumber���Word 用 python-docx，TXT 直接读
4. 实现匹配度评分（`matcher.py`）：关键词+权重规则引擎
5. 实现学习路线 & 面试辅导（`learning.py`）：��于差距分阶段生成 + 针对性追问
6. 实现 FastAPI 应用（`main.py`）：`create_app()` 工厂模式，`SERVE_STATIC` 环境变量切换本地/线上
7. 实现 Vue 3 渐进式前端（`index.html` + `app.js` + `styles.css`���：SVG 分数环��步骤切换、Markdown 下载
8. 本地端到端验证通过（样例简历分析正确）
9. Git 初始化、`.gitignore`、`README.md`

### Vercel 部署改造

1. 前端静态文件移至项目根目录（Vercel 直接托管）
2. 新增 `api/index.py`（Mangum 包装 FastAPI）
3. `backend/` 代码全部移入 `api/` 目录（Vercel 自动打包）
4. 仓库推送到 GitHub（https://github.com/yicLionel/Easy-Job-Tutor-Web）

## 五、部署排错全记录（重点）

本项目经历 6 次构建失败才摸清 Vercel Python 部署的完整坑点。

### 问题 1：vercel.json includeFiles 格式错误

**现象**：
```
Error: The "includeFiles" property in vercel.json function configuration is invalid.
```

**原因**：`includeFiles` 需要字符串（glob pattern），我写成了 `["backend/**", "api/**"]`（数组）。

**修复**：改为字符串 `"backend/**"`。但这��是根本问题——后面发现正确做法不是 `includeFiles`。

**提交**：`5ff2072`

---

### 问题 2：functions pattern 不匹配

**现象**：
```
Error: The pattern "api/index.py" defined in functions doesn't match any Serverless Functions inside the api directory.
```

**原因**：���端代码在独立 `backend/` 目录，`api/index.py` 导入 `from backend.main import create_app` 在构建期失败，Vercel 无法将其构建成函数，因此 `functions` 块中声明 `api/index.py` 时找不到已注册的函数。

**修复**：把 `parser.py` / `matcher.py` / `learning.py` / `knowledge.py` / `main.py` 全部移到 `api/` 目录，与 `index.py` 同路径。Vercel 自动打包函数目录内所有文件。删除 `functions` 块（只保留 `build.env.PYTHON_VERSION=3.12`）。

**提交**：`1aef979`

---

### 问题 3：pdfplumber 版���约束无解

**现象**：
```
× No solution found when resolving dependencies:
  Because only pdfplumber<=0.11.10 is available and your project depends on pdfplumber>=0.40
```

**原因**：pdfplumber 是 0.x 版本号（最高 0.11.x），`>=0.40` 永远无法满足。**Vercel 现在用 `uv` 严格解析 Python 依赖**，不可能的约束直接 build 失败。

**修复**：改为锁本地真实版本 `pdfplumber==0.11.10`。所有依赖都用精确版本：

```
fastapi==0.141.1
mangum==0.21.0
python-multipart==0.0.32
pdfplumber==0.11.10
python-docx==1.2.0
```

**教训**：给 Vercel（uv）写 `requirements.txt` 一律用真实存在的版本号，不要虚构高下限。

**提交**：`0315361`

---

### 问题 4：Python 函数未��册（静态上线，API 404）

**现象**：线上 `GET /` → 200（静态首页上线），但 `/api`、`/api/health`、`/api/analyze` 全部返回 Vercel 的 HTML 404 页面。

**原因**：此前多次构建均失败，Vercel 保留陈旧部署——只有静态资源，没有 Python 函数。

**修复**：在 `vercel.json` 加 `functions` 块显式声明函数；同时设置 `maxDuration: 30`（默认 10s 不够 PDF 解析）。

**提交**：`a57b4dc`

---

### 问题 5（致命根因）：Mangum 不兼容 Vercel

**现象**：以上修复后，`/api` 从 NOT_FOUND 变成 `FUNCTION_INVOCATION_FAILED`，说明函数注册成功但运行时崩溃。

**根因**：本地检查 Mangum 源码——**整个包中没有 "vercel" 字样**。Mangum 是给 AWS Lambda (API Gateway) 用的，根本不认 Vercel 的请求格式。用 `Mangum(app)` 包装 FastAPI 部署到 Vercel，运行时必然崩溃。

**修复**：重写 `api/index.py`，改用 Vercel 原生 `Request/Response` handler——用 `request.body` + 标准库 `email` 模块解析 multipart 表单，`from vercel import Request, Response`（Vercel 运行时内置，无需加依赖）。纯逻辑模块（parser/matcher/learning/knowledge）完全复用。

后经进一步验证，`from vercel import Request, Response` 也存在兼容问题（Vercel 运行时可能没有此模块）。

**教训**：**Vercel 上部署 Python Web 框架，不要用任何 AWS 适配器（Mangum、AWS SDK 等）**。Vercel 有自己完整的 ASGI 原生支持。

**提交**：`2ae64da`（第一次修复）、`bb06fac`（ASGI 方案）

---

### 问题 6（当前）：ASGI 函数运行时崩溃（进行中）

**现象**：用 `app = create_app()`（FastAPI 实例）作为 Vercel ASGI 入口后，
- `/api` 可达 → 返回 `FUNCTION_INVOCATION_FAILED`
- `/api/health` 仍然 NOT_FOUND（Vercel 不自动路由子路径）

**当前架构**：
- `api/index.py`：导出 `app = create_app()`（FastAPI ASGI 实例），Vercel 自动检测
- `vercel.json`：加 `rewrites` 规则 `"/api/(.*)" → "/api"` 让子路径可达
- `api/main.py`：加全局异常处理器，把 traceback 暴露到响应体方便调试

**当前状态**：函数已注册（从 NOT_FOUND 到 FUNCTION_INVOCATION_FAILED 是重要突破），但运行时有未捕获的异常。待 `rewrites` + 异常处理器构建完成后诊断具体崩溃原因。

**提交**（最新）：`e968219`（ASGI + exception handler）

---

## 六、已知可复用经验总结

### Vercel Python 部署核心规则

1. **Python 依赖必须用真实版本号**（Vercel 用 `uv` 严格解析，无解的约束直接 build 失败）。
2. **不要用 Mangum**。Mangum 是 AWS Lambda 适配器，在 Vercel 上 100% 不兼容。
3. **Vercel 原生支持 ASGI**。在 `api/index.py` 顶层导出 `app = FastAPI()` 即��被自动识别为 ASGI 应用，无需任何适配器。
4. **Vercel 对 `api/` 下每个 `.py` 文件做文件路由**：`api/health.py` → `/api/health`、`api/analyze.py` → `/api/analyze`，无需在 `vercel.json` 里配 `rewrites`。**关键点**：当这些文件顶层导出 ASGI `app`（FastAPI 实例）时，Vercel 把请求以**完整路径**（如 `/api/health`）传给 ASGI scope，path **不剥离**，因此 FastAPI 内部的 `@app.get("/api/health")` 能正确匹配。这是本项目最终可用的方案（由 Codex 落地，见第六节续）。
5. **静态文件和函数独立部署。** 根目录的 `index.html` / `app.js` / `styles.css` 由 Vercel 静态托管，`api/` 下的是函数。构建失败时可能保留陈旧部署，静态和函数分开对待。
6. **GitHub 连接器（MCP）没有建仓权限**（返回 403）。建仓/推送请用本地 `gh` CLI（用户已登录、token 含 `repo` scope）。

### 本地开发命令

```bash
# 启动后端
cd api && uvicorn main:app --port 8000
# 或从根目录
uvicorn api.main:app --port 8000
```

### 验证部署

```bash
# 检查函数是否存活
curl https://<domain>.vercel.app/api/health
# 预期返回 JSON: {"status":"ok"}
```

## 六（续）、Codex 最终修复与上线验证

**时间**：2026-07-30 下午（前述全部部署排错之后）。

### Codex 的改动（提交 94d79e3 / ca4e5a3 / 85105d8）

1. **路由改为文件路由**：新增 `api/health.py`、`api/analyze.py`，每个文件都 `from api.main import create_app` 并导出 `app = create_app()`（完整 FastAPI 应用）。`vercel.json` 清空为零配置（仅靠文件路由，不再依赖 rewrites）。
2. **包内绝对导入**：`api/main.py` 用 `from api.parser import ...`、`api/matcher.py` 用 `from api.knowledge import ...`（依赖 `api/__init__.py` 包标记）。线上验证：Vercel 新版 Python 运行时把项目根加入 `sys.path`，绝对导入可用。
3. **依赖与版本管理**：根目录新增 `requirements.txt`（Vercel 从根目录读取）与 `.python-version=3.12`，`api/requirements.txt` 不再需要。
4. **测试**：新增 `tests/test_api_entrypoint.py`，断言三个入口都能 import、都含 `/api/health` 与 `/api/analyze` 路由，且 `vercel.json` 不含 `functions` 限制。

### 实测结果（2026-07-30）

- 本地 `python -m unittest tests.test_api_entrypoint`：**3/3 通过**。
- 线上 `curl https://easy-job-tutor-web.vercel.app/api/health` → `{"status":"ok"}`。
- 线上 `POST /api/analyze`（样例 JD + 简历）→ 正常返回：`role=AI Agent 开发`、`overall_score=60`、`gap_count=9`、`learning_path.phases=4`、`interview.base_questions=4`。

**结论**：站点已完整上线可用，前端渐进式四步交互（上传 → 分数环 → 查漏补缺 → 学习路线 & 面试辅导）后端全部打通。

## 七、待办 / 可扩展方向

- [ ] **接入大模型做语义级匹配**：当前匹配度基于关键词+权重规则。替换 `api/matcher.py` 的 `analyze()` 内部逻辑即可，前端无需改动。
- [ ] **简历扫描件 OCR**：当前只支持可复制文本的 PDF / Word。需集成 OCR 引擎（Tesseract / 云 API）。
- [ ] **用户账号 + 历史记录**：保存历史分析结果，支持回顾、对比。
- [ ] **更多岗位模板**：拓展到产品经理、后端开发、数据分析等。
- [ ] **面试辅导升级为模拟面试对话**：从单向的问答列表升级为交互式对话。
- [ ] **GitHub Actions 自动部署**：push 后自动构建并部署到 Vercel。
