# Easy Job Tutor AI Product Interview Corpus Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reproducible, source-aware offline pipeline that turns current official AI product-manager requirements and recent community interview accounts into a deduplicated, reviewable, versioned corpus snapshot without copying post bodies.

**Architecture:** Store collection manifests and structured candidate records as append-only JSONL, transform them through pure normalization, deduplication, weighting, and validation functions, then require an explicit review decision before publishing a runtime snapshot. The web application reads only the published snapshot contract from the core plan; no collection tool runs in a user request.

**Tech Stack:** TypeScript 7.0.2, Zod 4.4.3, Node.js 22.23+, Vitest 4.1.10, `tsx`, agent-reach for source discovery, and version-controlled JSON/JSONL artifacts.

## Global Constraints

- Official JDs and official technical material define the capability taxonomy; they do not prove interview frequency.
- Community sources provide observed interview-event signals only.
- Use a primary window of the latest 12 months at collection time.
- Collect at most 20 candidate posts per platform from 牛客、小红书、知乎; do not merge the three platforms into one top-20 list.
- Use popularity only to prioritize candidate collection; never use likes as interview frequency.
- Count one cross-posted or reposted interview event once.
- Weight 12–24-month records down; exclude older records from current ranking.
- Preserve source URL, platform, query, publication/interview date, collection date, sample size, and confidence.
- Store structured paraphrases, not post bodies, long excerpts, or copied answer guides.
- Label inaccessible, inferred, marketing, aggregate, and first-hand status.
- Do not call an AI-structured corpus human-reviewed.
- Sponsored state never affects taxonomy, frequency, gap priority, natural resource ordering, or retest.

---

## File and Artifact Map

```text
content/
  corpus/
    manifests/
      ai-pm-zh-2026-07.json
    candidates/
      official.jsonl
      nowcoder.jsonl
      xiaohongshu.jsonl
      zhihu.jsonl
    reviews/
      ai-pm-zh-v1.decisions.jsonl
      ai-pm-zh-v1.review-summary.md
    taxonomy/
      ai-pm-zh-v1.json
    evaluation/
      cases.json
      reviewer-sheet.csv
data/
  corpus/
    snapshots/
      ai-pm-zh-v1-candidate.json
      ai-pm-zh-v1.json
scripts/
  corpus/
    schemas.ts
    import-candidates.ts
    normalize.ts
    deduplicate.ts
    score.ts
    validate.ts
    apply-reviews.ts
    publish.ts
    audit-sources.ts
tests/
  unit/corpus-pipeline/
  integration/corpus-pipeline/
docs/
  corpus/
    methodology.md
    source-audit.md
```

Candidate files contain source metadata and paraphrased topics only. The reviewed runtime snapshot is generated, never hand-edited.

---

### Task 1: Collection Manifest and Capability Taxonomy

**Files:**
- Create: `scripts/corpus/schemas.ts`
- Create: `content/corpus/manifests/ai-pm-zh-2026-07.json`
- Create: `content/corpus/taxonomy/ai-pm-zh-v1.json`
- Create: `docs/corpus/methodology.md`
- Test: `tests/unit/corpus-pipeline/schemas.test.ts`

**Interfaces:**
- Consumes: core `CorpusSnapshotSchema`.
- Produces:
  - `CollectionManifestSchema`
  - `CandidateRecordSchema`
  - `ReviewDecisionSchema`
  - `TaxonomyFileSchema`

- [ ] **Step 1: Write schema tests**

```ts
it("requires a fixed query and per-platform limit", () => {
  const manifest = CollectionManifestSchema.parse(fixtureManifest());
  expect(manifest.platforms.every((item) => item.maxCandidates === 20)).toBe(true);
  expect(manifest.queries.nowcoder.length).toBeGreaterThan(0);
});

it("rejects taxonomy claims that label an official source as frequency evidence", () => {
  const invalid = taxonomyFixture({ officialSourceRole: "frequency" });
  expect(() => TaxonomyFileSchema.parse(invalid)).toThrow();
});
```

- [ ] **Step 2: Verify failure**

Run: `pnpm vitest run tests/unit/corpus-pipeline/schemas.test.ts`
Expected: FAIL because collection schemas do not exist.

- [ ] **Step 3: Implement exact collection boundaries**

The manifest fixes:

```json
{
  "role": "ai_product_manager_intern_campus_zh",
  "collectedAt": "2026-07-30",
  "primaryWindowDays": 365,
  "supplementWindowDays": 730,
  "platforms": [
    { "id": "nowcoder", "maxCandidates": 20 },
    { "id": "xiaohongshu", "maxCandidates": 20 },
    { "id": "zhihu", "maxCandidates": 20 }
  ],
  "queries": {
    "nowcoder": ["AI 产品经理 实习 面经", "大模型 产品经理 校招 面经"],
    "xiaohongshu": ["AI 产品经理 面试", "大模型产品经理 校招"],
    "zhihu": ["AI 产品经理 面经", "大模型产品经理 面试题"]
  }
}
```

Taxonomy topics must include at least `project_depth`, `agent_vs_workflow`, `rag_and_retrieval`, `evaluation_badcase`, `model_selection`, `product_design`, `business_value`, `commercialization`, `privacy_safety`, and `stakeholder_delivery`. Every topic carries official source references, a definition, inclusion examples, exclusion examples, and no frequency claim.

- [ ] **Step 4: Verify schemas and methodology**

Run: `pnpm vitest run tests/unit/corpus-pipeline/schemas.test.ts && pnpm corpus:validate -- --manifest-only`
Expected: PASS with three separate platform limits and official-source role enforcement.

- [ ] **Step 5: Commit**

```bash
git add scripts/corpus/schemas.ts content/corpus/manifests content/corpus/taxonomy docs/corpus/methodology.md tests/unit/corpus-pipeline/schemas.test.ts
git commit -m "feat(corpus): define collection and taxonomy contracts"
```

---

### Task 2: Source Discovery and Structured Candidate Import

**Files:**
- Create: `scripts/corpus/import-candidates.ts`
- Create: `scripts/corpus/normalize.ts`
- Create: `content/corpus/candidates/official.jsonl`
- Create: `content/corpus/candidates/nowcoder.jsonl`
- Create: `content/corpus/candidates/xiaohongshu.jsonl`
- Create: `content/corpus/candidates/zhihu.jsonl`
- Test: `tests/unit/corpus-pipeline/normalize.test.ts`
- Test: `tests/integration/corpus-pipeline/import.test.ts`

**Interfaces:**
- Consumes: collection manifest and source-discovery results.
- Produces normalized `CandidateRecord` JSONL with no copied body.

- [ ] **Step 1: Write normalization and copyright-boundary tests**

```ts
it("stores a paraphrased topic without a post body", () => {
  const record = normalizeCandidate(rawCandidate());
  expect(record).not.toHaveProperty("body");
  expect(record.paraphrasedTopics[0].summary.length).toBeLessThanOrEqual(160);
  expect(record.source.url).toMatch(/^https:\/\//);
});

it("rejects more than twenty candidates for one platform", async () => {
  await expect(importCandidates(arrayOfCandidates(21, "nowcoder"))).rejects.toThrow(
    "PLATFORM_CANDIDATE_LIMIT",
  );
});
```

- [ ] **Step 2: Verify failure**

Run: `pnpm vitest run tests/unit/corpus-pipeline/normalize.test.ts tests/integration/corpus-pipeline/import.test.ts`
Expected: FAIL because importer and candidate files do not exist.

- [ ] **Step 3: Discover and record candidates**

Use `agent-reach` with the fixed manifest queries. For official records, use current official company recruitment pages and official technical documentation. For community records:

- retain the exact result URL and title;
- record result position and visible engagement only as `collectionPriority`;
- determine `first_hand`, `probable_first_hand`, `aggregate`, `marketing`, or `unknown`;
- paraphrase each observed question into taxonomy topics;
- record access status without bypassing login or CAPTCHA;
- omit source text when the page cannot be lawfully or reliably read;
- never fabricate missing interview dates, companies, or rounds.

Import records through:

```bash
pnpm corpus:import -- --manifest content/corpus/manifests/ai-pm-zh-2026-07.json
```

- [ ] **Step 4: Verify imported boundaries**

Run: `pnpm vitest run tests/unit/corpus-pipeline/normalize.test.ts tests/integration/corpus-pipeline/import.test.ts && pnpm corpus:validate -- --stage=candidates`
Expected: PASS; every platform has at most 20 candidates, every topic is paraphrased, and inaccessible fields remain explicitly unknown.

- [ ] **Step 5: Commit**

```bash
git add scripts/corpus/import-candidates.ts scripts/corpus/normalize.ts content/corpus/candidates tests/unit/corpus-pipeline/normalize.test.ts tests/integration/corpus-pipeline/import.test.ts package.json
git commit -m "data(corpus): import source-aware interview candidates"
```

---

### Task 3: Event Deduplication, Time Decay, and Platform Balance

**Files:**
- Create: `scripts/corpus/deduplicate.ts`
- Create: `scripts/corpus/score.ts`
- Test: `tests/unit/corpus-pipeline/deduplicate.test.ts`
- Test: `tests/unit/corpus-pipeline/score.test.ts`
- Test: `tests/fixtures/corpus-pipeline/cross-posts.json`

**Interfaces:**
- Consumes: normalized candidate records.
- Produces:
  - `deduplicateCandidates(records): DeduplicatedEvent[]`
  - `scoreTopicSignals(events, asOf): TopicSignal[]`

- [ ] **Step 1: Write cross-post and time-window tests**

```ts
it("counts a cross-platform repost as one interview event", () => {
  const events = deduplicateCandidates(crossPostFixture);
  expect(events).toHaveLength(1);
  expect(events[0].sourceUrls).toHaveLength(2);
});

it("downweights 12-24 month events and excludes older events", () => {
  const signals = scoreTopicSignals(
    [eventAtDaysAgo(100), eventAtDaysAgo(500), eventAtDaysAgo(800)],
    "2026-07-30",
  );
  expect(signals[0].eventWeights).toEqual([1, 0.5]);
});
```

- [ ] **Step 2: Verify failure**

Run: `pnpm vitest run tests/unit/corpus-pipeline/deduplicate.test.ts tests/unit/corpus-pipeline/score.test.ts`
Expected: FAIL because deduplication and scoring are missing.

- [ ] **Step 3: Implement deterministic event scoring**

Generate a candidate dedupe key from normalized company, role, round, event/publication month, and sorted topic IDs. Allow a review override to merge or split groups.

Use:

```ts
const recencyWeight = ageDays <= 365 ? 1 : ageDays <= 730 ? 0.5 : 0;
const evidenceWeight = {
  first_hand: 1,
  probable_first_hand: 0.75,
  aggregate: 0.3,
  marketing: 0.1,
  unknown: 0.2,
}[evidenceClass];
```

Cap one platform's contribution to a topic at 40% after at least two platforms contribute. Keep uncapped and capped values for audit. Likes and favorites never appear in this formula.

- [ ] **Step 4: Verify deterministic scoring**

Run: `pnpm vitest run tests/unit/corpus-pipeline/deduplicate.test.ts tests/unit/corpus-pipeline/score.test.ts`
Expected: PASS for cross-posts, manual overrides, recency, evidence class, platform cap, and stable tie-breaking.

- [ ] **Step 5: Commit**

```bash
git add scripts/corpus/deduplicate.ts scripts/corpus/score.ts tests/unit/corpus-pipeline tests/fixtures/corpus-pipeline
git commit -m "feat(corpus): deduplicate and weight interview events"
```

---

### Task 4: Review Decisions and Candidate Snapshot

**Files:**
- Create: `scripts/corpus/apply-reviews.ts`
- Create: `scripts/corpus/validate.ts`
- Create: `content/corpus/reviews/ai-pm-zh-v1.decisions.jsonl`
- Create: `content/corpus/reviews/ai-pm-zh-v1.review-summary.md`
- Create: `data/corpus/snapshots/ai-pm-zh-v1-candidate.json`
- Test: `tests/unit/corpus-pipeline/reviews.test.ts`
- Test: `tests/integration/corpus-pipeline/candidate-snapshot.test.ts`

**Interfaces:**
- Consumes: deduplicated events and explicit review decisions.
- Produces an `editorial_candidate` artifact that cannot be loaded as a `reviewed` runtime snapshot.

- [ ] **Step 1: Write review-state tests**

```ts
it("cannot promote an AI-structured record without an explicit human decision", () => {
  const result = applyReviews(events(), []);
  expect(result.publishable).toBe(false);
  expect(result.unreviewedIds).toHaveLength(events().length);
});

it("preserves rejected records in the audit trail", () => {
  const result = applyReviews(events(), [reject("event-1", "marketing")]);
  expect(result.audit.rejected[0].id).toBe("event-1");
  expect(result.runtimeEvents).not.toContainEqual(expect.objectContaining({ id: "event-1" }));
});
```

- [ ] **Step 2: Verify failure**

Run: `pnpm vitest run tests/unit/corpus-pipeline/reviews.test.ts tests/integration/corpus-pipeline/candidate-snapshot.test.ts`
Expected: FAIL because review application and candidate snapshot are absent.

- [ ] **Step 3: Build the review queue without self-approving it**

Generate decisions with `pending` status for every event and a review summary containing:

- source and access status;
- paraphrased topics;
- proposed dedupe group;
- evidence class;
- reason for inclusion/exclusion;
- original and capped frequency contribution.

Create `ai-pm-zh-v1-candidate.json` with `status: "editorial_candidate"`. Do not rename it to the runtime `ai-pm-zh-v1.json` until a human reviewer has recorded accept/reject decisions.

- [ ] **Step 4: Verify the review gate**

Run: `pnpm vitest run tests/unit/corpus-pipeline/reviews.test.ts tests/integration/corpus-pipeline/candidate-snapshot.test.ts && pnpm corpus:validate -- --stage=review`
Expected: PASS while publication remains blocked for pending decisions.

- [ ] **Step 5: Commit**

```bash
git add scripts/corpus/apply-reviews.ts scripts/corpus/validate.ts content/corpus/reviews data/corpus/snapshots/ai-pm-zh-v1-candidate.json tests/unit/corpus-pipeline/reviews.test.ts tests/integration/corpus-pipeline/candidate-snapshot.test.ts
git commit -m "data(corpus): prepare auditable human review queue"
```

---

### Task 5: Reviewed Snapshot Publication and Runtime Integration

**Files:**
- Create: `scripts/corpus/publish.ts`
- Create: `scripts/corpus/audit-sources.ts`
- Create: `data/corpus/snapshots/ai-pm-zh-v1.json`
- Create: `docs/corpus/source-audit.md`
- Test: `tests/integration/corpus-pipeline/publish.test.ts`
- Modify: `src/modules/corpus/domain.ts`
- Modify: `src/server/runtime/file-corpus-repository.ts`

**Interfaces:**
- Consumes: complete human decisions and candidate artifact.
- Produces reviewed `CorpusSnapshot` and source audit.

- [ ] **Step 1: Write publication-gate tests**

```ts
it("refuses publication with one pending decision", async () => {
  await expect(publishSnapshot(reviewSet({ pending: 1 }))).rejects.toThrow(
    "HUMAN_REVIEW_INCOMPLETE",
  );
});

it("embeds the snapshot id in every derived topic signal", async () => {
  const snapshot = await publishSnapshot(reviewSet({ pending: 0 }));
  expect(snapshot.topicSignals.every((item) => item.snapshotId === snapshot.id)).toBe(true);
});
```

- [ ] **Step 2: Verify failure**

Run: `pnpm vitest run tests/integration/corpus-pipeline/publish.test.ts`
Expected: FAIL because publication is missing.

- [ ] **Step 3: Implement publication and source audit**

Publication must:

1. verify every candidate has a human decision;
2. exclude rejected and inaccessible-without-evidence records;
3. rerun dedupe and scores from source records;
4. validate the core runtime snapshot schema;
5. write atomically to `ai-pm-zh-v1.json`;
6. output counts by platform, evidence class, topic, time window, access status, and decision.

If human decisions are not yet available, keep this task blocked at Step 3 and let the app use the clearly labeled demo snapshot. Do not generate a fake reviewed file.

- [ ] **Step 4: Verify publication or document the honest gate**

Run: `pnpm corpus:publish -- --version=ai-pm-zh-v1 && pnpm vitest run tests/integration/corpus-pipeline/publish.test.ts`
Expected when reviews are complete: PASS and a schema-valid reviewed snapshot.
Expected when reviews are pending: command exits non-zero with `HUMAN_REVIEW_INCOMPLETE`, and no reviewed file is created.

- [ ] **Step 5: Commit**

```bash
git add scripts/corpus/publish.ts scripts/corpus/audit-sources.ts src/modules/corpus/domain.ts src/server/runtime/file-corpus-repository.ts docs/corpus/source-audit.md tests/integration/corpus-pipeline/publish.test.ts data/corpus/snapshots/ai-pm-zh-v1.json
git commit -m "feat(corpus): publish reviewed interview snapshot"
```

Only include `data/corpus/snapshots/ai-pm-zh-v1.json` if Step 4 proves the review gate passed.

---

### Task 6: Content Evaluation Set and Reviewer Handoff

**Files:**
- Create: `content/corpus/evaluation/cases.json`
- Create: `content/corpus/evaluation/reviewer-sheet.csv`
- Create: `docs/content-evaluation/ai-pm-v1-protocol.md`
- Create: `scripts/corpus/create-reviewer-sheet.ts`
- Test: `tests/unit/corpus-pipeline/evaluation-cases.test.ts`

**Interfaces:**
- Consumes: taxonomy and candidate/reviewed snapshot.
- Produces 30–50 labeled evaluation cases and a two-reviewer comparison sheet.

- [ ] **Step 1: Write case-quality tests**

```ts
it("requires every case to label synthetic versus anonymized provenance", () => {
  const cases = EvaluationCaseSetSchema.parse(caseFixture());
  expect(cases.items.every((item) => ["synthetic", "anonymized"].includes(item.provenance))).toBe(
    true,
  );
});

it("requires expected gap types without prescribing exact generated wording", () => {
  const item = caseFixture().items[0];
  expect(item.expectedGapTypes.length).toBeGreaterThan(0);
  expect(item).not.toHaveProperty("expectedModelAnswer");
});
```

- [ ] **Step 2: Verify failure**

Run: `pnpm vitest run tests/unit/corpus-pipeline/evaluation-cases.test.ts`
Expected: FAIL because the evaluation set does not exist.

- [ ] **Step 3: Create the evaluation protocol and sheet**

Build 30–50 cases spanning:

- strong evidence but weak expression;
- knowledge gap;
- product-case gap;
- interview-expression gap;
- core-experience gap;
- ambiguous JD;
- sparse resume;
- conflicting or pending facts;
- low-confidence community signal.

The reviewer sheet captures top-three relevance, priority, type, traceability, task feasibility, false-positive reason, and free-text rationale. It requires two independent reviewers; Codex-assisted prefill must be labeled and cannot fill the human-review columns.

- [ ] **Step 4: Validate the handoff**

Run: `pnpm vitest run tests/unit/corpus-pipeline/evaluation-cases.test.ts && pnpm tsx scripts/corpus/create-reviewer-sheet.ts`
Expected: PASS with 30–50 unique cases and a CSV containing two empty human-review columns per criterion.

- [ ] **Step 5: Commit**

```bash
git add content/corpus/evaluation docs/content-evaluation/ai-pm-v1-protocol.md scripts/corpus/create-reviewer-sheet.ts tests/unit/corpus-pipeline/evaluation-cases.test.ts
git commit -m "test(content): prepare independent gap review set"
```

---

## Spec Coverage Matrix

| Specification requirement | Corpus task |
|---|---|
| Official sources define taxonomy only | Task 1 |
| Three platforms, max 20 each | Tasks 1–2 |
| Recent 12 months primary, 12–24 months downweighted | Tasks 1, 3 |
| Popularity is collection priority, not frequency | Tasks 1–3 |
| Independent-event deduplication | Task 3 |
| Source URL, query, dates, access, confidence | Tasks 1–2 |
| Structured paraphrase without copied body | Task 2 |
| Marketing and aggregate downgrades | Tasks 2–3 |
| Human review before runtime publication | Tasks 4–5 |
| Versioned, auditable snapshot | Task 5 |
| 30–50 content evaluation cases and two reviewers | Task 6 |
| No runtime scraping | All tasks; the output is a static snapshot |

## Execution Order and Honest Stop Condition

Execute Tasks 1–4 while the core application proceeds after its snapshot-contract task. Task 5 can publish only after explicit human review decisions exist; until then, the correct artifact is the candidate snapshot and the app must remain on a visible demo snapshot. Task 6 can proceed before publication and provides the structured human-review handoff.
