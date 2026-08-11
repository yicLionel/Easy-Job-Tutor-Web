# Public Beta 保守否定范围设计

**状态：** 已批准  
**日期：** 2026-08-11  
**适用范围：** Web 公开 Beta 的简历证据识别、覆盖率与改写资格

## 背景

证据分类器曾尝试在 `never used Java and developed Python services` 这类协调句中，于 `and` 后恢复正向证据。五轮实现与独立审查证明：仅靠文本形状、大写、工具动词或扁平技术词表，无法同时可靠处理普通词义（如 `poetry`）和同一实体别名（如 `node`/`node.js`、`k8s`/`kubernetes`）。错误恢复会继续污染覆盖率和简历改写，违背公开 Beta 的事实安全原则。

## 方案比较

1. **删除协调句自动恢复（采用）。** `and` 不再切断前置否定；模糊句保守为 `not_found / explicit_negation`。优点是确定、可解释、不会把否定经历写成正向经历；代价是少量真实经历需要用户另行确认。
2. **建立分组实体本体并做词义消歧（暂缓）。** 可表达别名等价，但一周 Beta 没有足够语料、评测集和维护机制验证一词多义。
3. **调用 LLM 做句法/语义判断（暂缓）。** 增加成本、延迟和非确定性，也无法在当前发布周期建立可接受的回归基线。

## 已批准行为

- 任何处于本地否定范围内的技能关键词均返回 `not_found / explicit_negation`。
- `and`、技术词、大写、别名或工具动词都不能自动恢复为正向证据。
- `Never used Java and developed Python services.` 对 Python 也保守返回缺证据。
- `Never used poetry and developed RAG applications.` 不得产生 RAG 覆盖或改写。
- `Never used Node and developed Node.js services.` 与 `Never used k8s and developed Kubernetes services.` 不得把同一技术判为正向证据。
- 明确通过句号、分号、逗号或换行进入新的独立陈述时，沿用现有上下文边界判断；本设计不扩大边界规则。
- 事实分类结果继续作为覆盖率、事实台账和改写资格的唯一输入。

## 代码边界

- 从 `api/evidence.py` 删除协调重置与实体规范化逻辑，恢复为只判断否定范围。
- 从 `api/knowledge.py` 删除仅为协调重置服务的技术实体 allowlist。
- 从 `api/matcher.py` 删除 allowlist 传递层，所有消费者直接复用同一证据分类函数。
- 保留 `classify_skill_evidence(skill, resume_text) -> EvidenceMatch` 的两参数公共接口。

## 验收

- 新的分类器与 matcher 回归必须先在当前代码上失败，再以删除生产逻辑的方式通过。
- 所有否定反例均为 `not_found / explicit_negation`、覆盖率 0、无 rewrite。
- 原有明确正向项目动作、关键词列表 `uncertain`、短关键词边界和中英文否定测试保持通过。
- 聚焦测试、全量测试和 `git diff --check` 全部通过。

## 风险与后续

公开 Beta 接受协调句的保守漏判。只有在积累真实误判样本、建立标注评测集并定义实体/词义模型后，才重新评估自动恢复；不得通过新增正则特例恢复。
