# Notes: Easy Job Tutor 网页实现

## Authoritative Sources

- 产品规格：`docs/superpowers/specs/2026-07-30-easy-job-tutor-web-design.md`
- 设计规格提交：`ce5ebaf`
- 核心实施计划：`docs/superpowers/plans/2026-07-30-easy-job-tutor-web-core-mvp.md`
- 语料实施计划：`docs/superpowers/plans/2026-07-30-easy-job-tutor-corpus-pipeline.md`

## Current Environment

- Node.js：`v22.23.1`
- npm：`10.9.8`
- pnpm：`11.9.0`
- 根目录为独立 Git 仓库，默认分支 `main`

## Implementation Constraints

- 首个有用结果从点击分析开始计时；受控有效请求全部不超过 15 秒，p95 不超过 12 秒。
- 原始 PDF/DOCX 解析后删除；未确认事实不能进入最终材料。
- 语料运行时只读版本化快照，不实时抓取社区平台。
- 输入版本、请求 ID 与分析 ID 三重隔离过期异步结果。
- 第一版由平台调用模型；测试和无密钥本地演示需要明确标记的确定性测试适配器。

## Findings

- 默认 npm 缓存存在权限污染，依赖查询与安装必须使用项目专用缓存。
- 2026-07-30 从 npm registry 核验的当前稳定版本：
  - Next.js `16.2.12`
  - React `19.2.8`
  - TypeScript `7.0.2`
  - Tailwind CSS `4.3.3`
  - Vitest `4.1.10`
  - Playwright `1.62.0`
  - Drizzle ORM `0.45.2`
  - better-sqlite3 `13.0.2`
  - Zod `4.4.3`
  - Mammoth `1.12.0`
  - pdf-parse `2.4.5`
- 首版采用 pnpm 管理依赖；数据库使用单实例 SQLite + Drizzle，并通过 repository 接口保持可迁移性。
- 模型通过 OpenAI-compatible HTTP adapter 接入；测试与无密钥本地演示使用显式 `mock` 适配器，不能被描述为真实模型结果。
- Next.js 官方确认 `cookies()` 为异步 API，Cookie 写入必须发生在 Route Handler 或 Server Function 且在开始流式响应之前：https://nextjs.org/docs/app/api-reference/functions/cookies
- Drizzle 官方确认 `better-sqlite3` 是原生支持的 SQLite 驱动，迁移采用代码优先、生成并提交 SQL：https://orm.drizzle.team/docs/sqlite/get-started-sqlite 和 https://orm.drizzle.team/docs/migrations
- Playwright 官方建议用 `@axe-core/playwright` 检测自动可发现的可访问性问题，同时保留人工检查边界：https://playwright.dev/docs/accessibility-testing
