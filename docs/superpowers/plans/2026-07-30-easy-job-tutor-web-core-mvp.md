# Easy Job Tutor Web Core MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a locally runnable, responsive AI product-manager gap-closure web MVP with confirmed-fact gating, deterministic fast insights, progressive enrichment, seven-day tasks, practice/retest, anonymous recovery, deletion, and automated verification.

**Architecture:** Use a modular Next.js application with route handlers, a Node runtime, SQLite/Drizzle persistence, pure domain engines, and a provider-neutral model adapter. The browser consumes persisted analysis stages through SSE with polling fallback; the runtime reads only a versioned offline corpus snapshot and never scrapes community platforms in the request path.

**Tech Stack:** Node.js 22.23+, pnpm 11.9+, Next.js 16.2.12, React 19.2.8, TypeScript 7.0.2, Tailwind CSS 4.3.3, Zod 4.4.3, Drizzle ORM 0.45.2, better-sqlite3 13.0.2, Vitest 4.1.10, Playwright 1.62.0.

## Global Constraints

- The first release serves Chinese AI product-manager internships and campus recruiting only.
- Start `time_to_first_insight` when the user clicks analysis; every controlled valid request must render three real gaps and an overall judgment within 15 seconds, with `p95 <= 12 seconds`.
- Run deterministic gap analysis and the optional fast model call concurrently; cap the fast model budget at 8 seconds and persist `fast_insight_ready` by server second 12.
- Only `confirmed` facts can enter final resume suggestions, answer examples, or positive candidate evidence.
- Keep gap impact separate from short-term actionability; a seven-day plan cannot hide a high-impact core-experience gap.
- Use `input_version`, `request_id`, and `analysis_id`; stale work can remain historical but can never replace the current result.
- Read only an offline, reviewed, versioned corpus snapshot at runtime.
- Delete uploaded PDF/DOCX bytes after parsing; never log resume content, recovery codes, API keys, or complete model payloads.
- Use platform-side model calls; never ask the student for an API key.
- Never output hiring probability, ATS pass probability, or an uncalibrated magic score.
- Do not implement payments, sponsorship, auto-apply, voice interview, WYSIWYG resume editing, multiple job families, or Side Panel expansion.
- Treat automated tests as engineering evidence only; content validity and Beta user value remain separately labeled.

---

## File and Module Map

```text
src/
  app/
    api/
      beta/sessions/route.ts
      beta/recover/route.ts
      materials/route.ts
      materials/confirm/route.ts
      analyses/route.ts
      analyses/[analysisId]/route.ts
      analyses/[analysisId]/events/route.ts
      plans/[planId]/route.ts
      tasks/[taskId]/complete/route.ts
      practice/[questionId]/attempts/route.ts
      privacy/delete/route.ts
    invite/page.tsx
    workspace/materials/page.tsx
    workspace/analysis/page.tsx
    workspace/plan/page.tsx
    workspace/practice/page.tsx
    workspace/privacy/page.tsx
    globals.css
    layout.tsx
    page.tsx
  components/
    ui/
    invite/
    materials/
    analysis/
    plan/
    practice/
    privacy/
  modules/
    session/
    materials/
    facts/
    corpus/
    analysis/
    plans/
    practice/
    telemetry/
  server/
    ai/
    db/
    documents/
    http/
    runtime/
data/
  corpus/snapshots/
drizzle/
tests/
  unit/
  integration/
  e2e/
  fixtures/
```

Each `modules/<name>` directory owns its domain types and service interfaces. `server/*` contains adapters. Route handlers compose services through `src/server/runtime/container.ts`; React components call HTTP endpoints and never import database adapters.

---

### Task 1: Project Toolchain and Tested App Shell

**Files:**
- Create: `package.json`
- Create: `pnpm-lock.yaml`
- Create: `.npmrc`
- Create: `.gitignore`
- Create: `.env.example`
- Create: `next.config.ts`
- Create: `tsconfig.json`
- Create: `postcss.config.mjs`
- Create: `eslint.config.mjs`
- Create: `vitest.config.ts`
- Create: `vitest.setup.ts`
- Create: `playwright.config.ts`
- Create: `src/app/layout.tsx`
- Create: `src/app/page.tsx`
- Create: `src/app/globals.css`
- Test: `tests/unit/app/home-page.test.tsx`

**Interfaces:**
- Consumes: none.
- Produces: pnpm scripts `dev`, `build`, `lint`, `typecheck`, `test`, `test:unit`, `test:integration`, `test:e2e`, `db:generate`, `db:migrate`, `corpus:import`, `corpus:validate`, and `corpus:publish`; import alias `@/* -> src/*`.

- [ ] **Step 1: Write the failing smoke test**

```tsx
// @vitest-environment jsdom
import { render, screen } from "@testing-library/react";
import HomePage from "@/app/page";

it("states the gap-closure product contract", () => {
  render(<HomePage />);
  expect(
    screen.getByRole("heading", { name: "先看清差距，再决定怎么补" }),
  ).toBeInTheDocument();
  expect(screen.getByText("AI 产品经理实习与校招")).toBeInTheDocument();
});
```

- [ ] **Step 2: Run the test and record the expected failure**

Run: `pnpm vitest run tests/unit/app/home-page.test.tsx`
Expected: FAIL because the Next.js app and `HomePage` do not exist.

- [ ] **Step 3: Create the toolchain and minimal shell**

Create `package.json` with the pinned primary dependencies from the header and install auxiliary packages:

```bash
pnpm add next@16.2.12 react@19.2.8 react-dom@19.2.8 drizzle-orm@0.45.2 better-sqlite3@13.0.2 zod@4.4.3 mammoth@1.12.0 pdf-parse@2.4.5 lucide-react
pnpm add -D typescript@7.0.2 tailwindcss@4.3.3 @tailwindcss/postcss postcss vitest@4.1.10 jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event @playwright/test@1.62.0 @axe-core/playwright drizzle-kit @types/better-sqlite3 @types/node @types/react @types/react-dom eslint eslint-config-next tsx
```

Set `.npmrc` to `store-dir=.cache/pnpm-store`, ignore `.cache`, `.next`, `node_modules`, local databases, raw uploads, Playwright artifacts, and `.env*` except `.env.example`.

Define `test:unit` as `vitest run tests/unit`, `test:integration` as `vitest run tests/integration`, and `test` as both commands in sequence. Enable `resolveJsonModule`, strict mode, and `noUncheckedIndexedAccess` in `tsconfig.json`.

Implement a server-rendered home shell:

```tsx
export default function HomePage() {
  return (
    <main>
      <p>AI 产品经理实习与校招</p>
      <h1>先看清差距，再决定怎么补</h1>
      <p>用已确认的真实经历，对齐目标 JD、面试考点与七天准备任务。</p>
    </main>
  );
}
```

- [ ] **Step 4: Verify the shell**

Run: `pnpm test:unit && pnpm typecheck && pnpm lint && pnpm build`
Expected: all commands PASS and the production build contains `/`.

- [ ] **Step 5: Commit**

```bash
git add package.json pnpm-lock.yaml .npmrc .gitignore .env.example next.config.ts tsconfig.json postcss.config.mjs eslint.config.mjs vitest.config.ts vitest.setup.ts playwright.config.ts src/app tests/unit/app
git commit -m "chore(app): bootstrap tested web shell"
```

---

### Task 2: Versioned Corpus Snapshot Contract

**Files:**
- Create: `src/modules/corpus/domain.ts`
- Create: `src/modules/corpus/snapshot-repository.ts`
- Create: `src/server/runtime/file-corpus-repository.ts`
- Create: `data/corpus/snapshots/demo-ai-pm-v0.json`
- Create: `tests/fixtures/corpus/demo-snapshot.json`
- Test: `tests/unit/corpus/snapshot.test.ts`

**Interfaces:**
- Consumes: Zod.
- Produces:
  - `CorpusSnapshotSchema`
  - `type CorpusSnapshot`
  - `interface CorpusSnapshotRepository { getActive(): Promise<CorpusSnapshot>; getById(id: string): Promise<CorpusSnapshot | null> }`
  - `FileCorpusSnapshotRepository`

- [ ] **Step 1: Write contract tests**

```ts
import { CorpusSnapshotSchema } from "@/modules/corpus/domain";
import fixture from "../../fixtures/corpus/demo-snapshot.json";

it("accepts a traceable reviewed snapshot", () => {
  const snapshot = CorpusSnapshotSchema.parse(fixture);
  expect(snapshot.id).toBe("demo-ai-pm-v0");
  expect(snapshot.status).toBe("demo_unverified");
  expect(snapshot.events[0].source.url).toMatch(/^https:\/\//);
});

it("rejects an event without a source URL", () => {
  const invalid = structuredClone(fixture);
  delete invalid.events[0].source.url;
  expect(() => CorpusSnapshotSchema.parse(invalid)).toThrow();
});
```

- [ ] **Step 2: Verify failure**

Run: `pnpm vitest run tests/unit/corpus/snapshot.test.ts`
Expected: FAIL because the schemas and fixture do not exist.

- [ ] **Step 3: Implement the snapshot schema and file adapter**

Define exact status and confidence types:

```ts
export const CorpusSnapshotSchema = z.object({
  id: z.string().min(1),
  role: z.literal("ai_product_manager_intern_campus_zh"),
  status: z.enum(["demo_unverified", "reviewed"]),
  publishedAt: z.string().datetime(),
  window: z.object({ from: z.string().date(), to: z.string().date() }),
  topics: z.array(TaxonomyTopicSchema).min(1),
  events: z.array(InterviewEventSchema),
});
```

The demo snapshot must contain only clearly labeled synthetic events and three topics (`agent_workflow`, `rag_evaluation`, `product_case`) so the app can run before the reviewed corpus plan publishes `ai-pm-zh-v1`.

- [ ] **Step 4: Verify contract and loader**

Run: `pnpm vitest run tests/unit/corpus/snapshot.test.ts`
Expected: PASS, including missing-source and invalid-status cases.

- [ ] **Step 5: Commit**

```bash
git add src/modules/corpus src/server/runtime/file-corpus-repository.ts data/corpus/snapshots/demo-ai-pm-v0.json tests/fixtures/corpus tests/unit/corpus
git commit -m "feat(corpus): define versioned snapshot contract"
```

---

### Task 3: Confirmed Fact Ledger and Material Versions

**Files:**
- Create: `src/modules/facts/domain.ts`
- Create: `src/modules/facts/fact-ledger.ts`
- Create: `src/modules/materials/domain.ts`
- Create: `src/modules/materials/input-version.ts`
- Test: `tests/unit/facts/fact-ledger.test.ts`
- Test: `tests/unit/materials/input-version.test.ts`

**Interfaces:**
- Consumes: Node `crypto`.
- Produces:
  - `type FactStatus = "confirmed" | "pending_confirmation" | "model_inference"`
  - `type Fact`
  - `selectConfirmedFacts(facts: readonly Fact[]): Fact[]`
  - `assertFactsAllowed(factIds: readonly string[], facts: readonly Fact[]): void`
  - `computeInputVersion(input: ConfirmedMaterialInput): string`

- [ ] **Step 1: Write fact-gate and version tests**

```ts
it("allows only confirmed facts into final evidence", () => {
  const confirmed = selectConfirmedFacts([
    fact("f1", "confirmed"),
    fact("f2", "pending_confirmation"),
    fact("f3", "model_inference"),
  ]);
  expect(confirmed.map((item) => item.id)).toEqual(["f1"]);
});

it("changes input version when a confirmed fact changes", () => {
  const before = computeInputVersion(materialInput({ factText: "完成原型" }));
  const after = computeInputVersion(materialInput({ factText: "完成并验收原型" }));
  expect(after).not.toBe(before);
});
```

- [ ] **Step 2: Verify failure**

Run: `pnpm vitest run tests/unit/facts tests/unit/materials/input-version.test.ts`
Expected: FAIL because the ledger and canonical hash do not exist.

- [ ] **Step 3: Implement canonical hashing and gate**

Use stable key ordering and SHA-256:

```ts
export function computeInputVersion(input: ConfirmedMaterialInput): string {
  const canonical = JSON.stringify({
    jd: input.jd.normalizedText,
    resume: input.resume.normalizedText,
    facts: [...input.facts]
      .sort((a, b) => a.id.localeCompare(b.id))
      .map(({ id, text, status, sourceRef }) => ({ id, text, status, sourceRef })),
  });
  return createHash("sha256").update(canonical).digest("hex");
}
```

`assertFactsAllowed` must throw `UnconfirmedFactError` listing prohibited IDs.

- [ ] **Step 4: Verify deterministic behavior**

Run: `pnpm vitest run tests/unit/facts tests/unit/materials/input-version.test.ts`
Expected: PASS for confirmed-only selection, stable order, version changes, and prohibited IDs.

- [ ] **Step 5: Commit**

```bash
git add src/modules/facts src/modules/materials tests/unit/facts tests/unit/materials
git commit -m "feat(facts): enforce confirmed evidence ledger"
```

---

### Task 4: Deterministic Gap Ranking Engine

**Files:**
- Create: `src/modules/analysis/domain.ts`
- Create: `src/modules/analysis/gap-engine.ts`
- Create: `src/modules/analysis/overall-judgment.ts`
- Test: `tests/unit/analysis/gap-engine.test.ts`
- Test: `tests/unit/analysis/overall-judgment.test.ts`

**Interfaces:**
- Consumes: `Fact`, `CorpusSnapshot`.
- Produces:
  - `type GapType`
  - `type GapPriority = "P0" | "P1" | "P2"`
  - `type GapSignalInput`
  - `type RankedGap`
  - `rankGaps(inputs: readonly GapSignalInput[]): RankedGap[]`
  - `deriveOverallJudgment(gaps: readonly RankedGap[]): OverallJudgment`

- [ ] **Step 1: Write ranking invariants**

```ts
it("does not lower a hard core-experience gap because it is not quickly fixable", () => {
  const [gap] = rankGaps([
    signal({
      id: "core",
      hardRequirement: true,
      evidenceDeficit: 3,
      actionability: 0,
    }),
  ]);
  expect(gap.priority).toBe("P0");
  expect(gap.actionability).toBe(0);
});

it("uses taxonomy id as a stable final tie breaker", () => {
  const ranked = rankGaps([signal({ id: "z" }), signal({ id: "a" })]);
  expect(ranked.map((gap) => gap.topicId)).toEqual(["a", "z"]);
});
```

- [ ] **Step 2: Verify failure**

Run: `pnpm vitest run tests/unit/analysis/gap-engine.test.ts tests/unit/analysis/overall-judgment.test.ts`
Expected: FAIL because gap ranking is missing.

- [ ] **Step 3: Implement explicit signals**

Normalize all numeric signals to integers:

```ts
const impact =
  input.jdImportance * 4 +
  input.evidenceDeficit * 3 +
  input.interviewFrequency * 2 +
  input.sourceConfidence;

const priority: GapPriority =
  input.hardRequirement && input.evidenceDeficit >= 2
    ? "P0"
    : impact >= 24
      ? "P0"
      : impact >= 14
        ? "P1"
        : "P2";
```

Sort by priority, impact descending, source confidence descending, and topic ID. Preserve `actionability` as a separate field. Derive one of `expression_gap`, `short_term_preparation_gap`, or `core_capability_gap` from the highest-impact gap types and include trigger IDs.

- [ ] **Step 4: Verify ranking and judgment**

Run: `pnpm vitest run tests/unit/analysis`
Expected: PASS for hard gaps, tie-breaking, separate actionability, and non-probabilistic judgments.

- [ ] **Step 5: Commit**

```bash
git add src/modules/analysis tests/unit/analysis
git commit -m "feat(analysis): rank explainable role gaps"
```

---

### Task 5: Seven-Day Plan and Retest Domain

**Files:**
- Create: `src/modules/plans/domain.ts`
- Create: `src/modules/plans/plan-engine.ts`
- Create: `src/modules/practice/domain.ts`
- Create: `src/modules/practice/retest-engine.ts`
- Test: `tests/unit/plans/plan-engine.test.ts`
- Test: `tests/unit/practice/retest-engine.test.ts`

**Interfaces:**
- Consumes: `RankedGap`, confirmed facts.
- Produces:
  - `buildSevenDayPlan(gaps: readonly RankedGap[], dailyMinutes: DailyMinutes): PreparationPlan`
  - `validateTaskTraceability(task: PreparationTask): void`
  - `applyRetest(previous: ReadinessState, attempt: PracticeAttempt, rubric: RetestRubric): RetestResult`

- [ ] **Step 1: Write task and retest tests**

```ts
it("binds every top gap to a deliverable and retest", () => {
  const plan = buildSevenDayPlan(topThreeGaps(), 30);
  for (const gap of topThreeGaps()) {
    expect(plan.tasks.some((task) => task.gapIds.includes(gap.id))).toBe(true);
  }
  expect(plan.tasks.every((task) => task.deliverable && task.retestRubricId)).toBe(true);
});

it("never turns practice performance into confirmed work experience", () => {
  const result = applyRetest(state(), attempt({ passed: true }), rubric());
  expect(result.factMutations).toEqual([]);
  expect(result.readinessDelta).toBeGreaterThan(0);
});
```

- [ ] **Step 2: Verify failure**

Run: `pnpm vitest run tests/unit/plans tests/unit/practice`
Expected: FAIL because plan and retest engines do not exist.

- [ ] **Step 3: Implement capacity-aware scheduling**

Accept `15 | 30 | 60 | 90 | number` daily minutes, reject values outside `15..240`, and fill seven days without exceeding daily capacity. A `core_experience` P0 receives an honest long-horizon action and remains visible even if it cannot fit in seven days.

Every task must have:

```ts
type PreparationTask = {
  id: string;
  gapIds: string[];
  objective: string;
  estimatedMinutes: number;
  resourceRefs: string[];
  deliverable: string;
  completionRule: string;
  retestRubricId: string;
  day: 1 | 2 | 3 | 4 | 5 | 6 | 7;
};
```

- [ ] **Step 4: Verify plan invariants**

Run: `pnpm vitest run tests/unit/plans tests/unit/practice`
Expected: PASS for traceability, daily capacity, core-gap visibility, and no fact promotion.

- [ ] **Step 5: Commit**

```bash
git add src/modules/plans src/modules/practice tests/unit/plans tests/unit/practice
git commit -m "feat(plan): create traceable preparation and retest flow"
```

---

### Task 6: SQLite Schema, Migrations, and Repository Adapters

**Files:**
- Create: `drizzle.config.ts`
- Create: `src/server/db/client.ts`
- Create: `src/server/db/schema/session.ts`
- Create: `src/server/db/schema/materials.ts`
- Create: `src/server/db/schema/analysis.ts`
- Create: `src/server/db/schema/plans.ts`
- Create: `src/server/db/schema/corpus.ts`
- Create: `src/server/db/schema/index.ts`
- Create: `src/server/db/migrate.ts`
- Create: `src/server/db/repositories/session-repository.ts`
- Create: `src/server/db/repositories/material-repository.ts`
- Create: `src/server/db/repositories/analysis-repository.ts`
- Create: `src/server/db/repositories/plan-repository.ts`
- Create: `src/server/db/repositories/practice-repository.ts`
- Create: `drizzle/0000_initial.sql`
- Test: `tests/integration/db/repositories.test.ts`

**Interfaces:**
- Consumes: domain types from Tasks 2–5.
- Produces database-backed repository implementations and `createDatabase(path: string)`.

- [ ] **Step 1: Write repository integration tests**

```ts
it("keeps a stale analysis historical without changing the active pointer", async () => {
  const first = await repository.createAnalysis(record({ inputVersion: "v1" }));
  await repository.activate(first.id, "v1");
  const second = await repository.createAnalysis(record({ inputVersion: "v2" }));
  await repository.activate(second.id, "v2");

  await repository.appendStage(first.id, "fast_insight_ready", "v1", payload());

  expect((await repository.getCurrent(sessionId)).id).toBe(second.id);
  expect(await repository.getById(first.id)).not.toBeNull();
});
```

- [ ] **Step 2: Verify failure**

Run: `pnpm vitest run tests/integration/db/repositories.test.ts`
Expected: FAIL because database schema and repositories are missing.

- [ ] **Step 3: Define normalized tables and generated migration**

Use text UUID primary keys, integer timestamps, JSON text only for immutable payload snapshots, foreign keys, and indexes on session/current version, analysis/request ID, analysis/input version, and event sequence. Enforce unique `(session_id, idempotency_key)`.

Generate and inspect migration:

```bash
pnpm drizzle-kit generate --name initial
pnpm drizzle-kit migrate
```

Repository writes that mark a stage ready must update payload and append the event in one transaction.

- [ ] **Step 4: Verify persistence and migration**

Run: `pnpm db:migrate && pnpm vitest run tests/integration/db/repositories.test.ts`
Expected: PASS for round trips, transactions, unique idempotency, active version, and foreign keys.

- [ ] **Step 5: Commit**

```bash
git add drizzle.config.ts drizzle src/server/db tests/integration/db package.json pnpm-lock.yaml
git commit -m "feat(db): persist versioned product workflow"
```

---

### Task 7: Anonymous Beta Session and Recovery

**Files:**
- Create: `src/modules/session/domain.ts`
- Create: `src/modules/session/session-service.ts`
- Create: `src/server/http/session-cookie.ts`
- Create: `src/app/api/beta/sessions/route.ts`
- Create: `src/app/api/beta/recover/route.ts`
- Test: `tests/unit/session/session-service.test.ts`
- Test: `tests/integration/api/session-routes.test.ts`

**Interfaces:**
- Consumes: `SessionRepository`.
- Produces:
  - `SessionService.create(inviteCode): Promise<{ sessionId; sessionToken; recoveryCode }>`
  - `SessionService.recover(recoveryCode): Promise<{ sessionToken }>`
  - `SessionService.rotateRecovery(sessionId): Promise<{ recoveryCode }>`
  - cookie name `ejt_session`.

- [ ] **Step 1: Write recovery security tests**

```ts
it("stores only a salted recovery-code digest", async () => {
  const created = await service.create("VALID-BETA");
  const stored = await repository.get(created.sessionId);
  expect(stored?.recoveryCodeDigest).not.toContain(created.recoveryCode);
});

it("invalidates the old code after rotation", async () => {
  const created = await service.create("VALID-BETA");
  const rotated = await service.rotateRecovery(created.sessionId);
  await expect(service.recover(created.recoveryCode)).rejects.toThrow("RECOVERY_INVALID");
  await expect(service.recover(rotated.recoveryCode)).resolves.toBeDefined();
});
```

- [ ] **Step 2: Verify failure**

Run: `pnpm vitest run tests/unit/session tests/integration/api/session-routes.test.ts`
Expected: FAIL because the service and routes do not exist.

- [ ] **Step 3: Implement scrypt digests and secure cookie creation**

Use `randomBytes(24)` for opaque values, `scrypt` with a per-code random salt, and `timingSafeEqual`. Set the cookie in the route handler before any stream:

```ts
response.cookies.set("ejt_session", sessionToken, {
  httpOnly: true,
  secure: process.env.NODE_ENV === "production",
  sameSite: "lax",
  path: "/",
  maxAge: 60 * 60 * 24 * 14,
});
```

Rate-limit create and recover attempts by invite/session/IP hash without persisting raw IP.

- [ ] **Step 4: Verify sessions**

Run: `pnpm vitest run tests/unit/session tests/integration/api/session-routes.test.ts`
Expected: PASS for invite limits, one-time recovery display, rotation, cookie options, and invalid code handling.

- [ ] **Step 5: Commit**

```bash
git add src/modules/session src/server/http/session-cookie.ts src/app/api/beta tests/unit/session tests/integration/api/session-routes.test.ts
git commit -m "feat(session): add anonymous beta recovery"
```

---

### Task 8: Secure Document Parsing and Material Confirmation

**Files:**
- Create: `src/server/documents/types.ts`
- Create: `src/server/documents/validate-upload.ts`
- Create: `src/server/documents/parse-pdf.ts`
- Create: `src/server/documents/parse-docx.ts`
- Create: `src/server/documents/parse-upload.ts`
- Create: `src/modules/materials/material-service.ts`
- Create: `src/app/api/materials/route.ts`
- Create: `src/app/api/materials/confirm/route.ts`
- Test: `tests/unit/documents/validate-upload.test.ts`
- Test: `tests/integration/documents/parse-upload.test.ts`
- Test: `tests/integration/api/material-routes.test.ts`
- Fixture: `tests/fixtures/documents/sample-resume.pdf`
- Fixture: `tests/fixtures/documents/sample-resume.docx`

**Interfaces:**
- Consumes: `MaterialRepository`, `computeInputVersion`.
- Produces:
  - `parseUploadedDocument(input: UploadInput): Promise<ParsedDocument>`
  - `MaterialService.confirm(sessionId, draftId, edits): Promise<ConfirmedMaterialSet>`

- [ ] **Step 1: Write deletion and confirmation tests**

```ts
it("removes temporary bytes after a successful parse", async () => {
  const tracker = tempTracker();
  await parseUploadedDocument(pdfUpload(), { tempTracker: tracker });
  expect(await tracker.remainingFiles()).toEqual([]);
});

it("removes temporary bytes after a parser failure", async () => {
  const tracker = tempTracker();
  await expect(parseUploadedDocument(corruptPdf(), { tempTracker: tracker })).rejects.toThrow();
  expect(await tracker.remainingFiles()).toEqual([]);
});
```

- [ ] **Step 2: Verify failure**

Run: `pnpm vitest run tests/unit/documents tests/integration/documents tests/integration/api/material-routes.test.ts`
Expected: FAIL because document handlers do not exist.

- [ ] **Step 3: Implement bounded parsing**

Accept PDF and DOCX up to 5 MiB, verify extension plus magic bytes, create a request-specific directory with `mkdtemp`, parse using `pdf-parse` or `mammoth`, normalize Unicode/newlines, and remove the explicit temporary directory in `finally`.

The upload route returns a draft only. The confirmation route persists edited normalized text, creates candidate facts with `pending_confirmation`, and increments `input_version` only after confirmation.

- [ ] **Step 4: Verify parsing and routes**

Run: `pnpm vitest run tests/unit/documents tests/integration/documents tests/integration/api/material-routes.test.ts`
Expected: PASS for PDF, DOCX, pasted text, signature mismatch, size limit, parser failure, cleanup, and confirmation.

- [ ] **Step 5: Commit**

```bash
git add src/server/documents src/modules/materials/material-service.ts src/app/api/materials tests/unit/documents tests/integration/documents tests/integration/api/material-routes.test.ts tests/fixtures/documents
git commit -m "feat(materials): parse and confirm private inputs"
```

---

### Task 9: Provider-Neutral Structured Model Adapter

**Files:**
- Create: `src/server/ai/model-adapter.ts`
- Create: `src/server/ai/openai-compatible-adapter.ts`
- Create: `src/server/ai/mock-model-adapter.ts`
- Create: `src/server/ai/output-guard.ts`
- Create: `src/server/ai/concurrency-limiter.ts`
- Test: `tests/unit/ai/output-guard.test.ts`
- Test: `tests/integration/ai/model-adapter.test.ts`

**Interfaces:**
- Consumes: Zod, confirmed facts, valid source IDs.
- Produces:
  - `type ModelResult<T> = { data: T; provenance: { provider: string; model: string; realModel: boolean } }`
  - `ModelAdapter.completeStructured<T>(request: StructuredRequest<T>): Promise<ModelResult<T>>`
  - `OpenAICompatibleAdapter`
  - `MockModelAdapter`
  - `guardModelOutput(output, context): GuardedOutput`

- [ ] **Step 1: Write timeout and hallucinated-reference tests**

```ts
it("rejects unknown fact and source ids", () => {
  expect(() =>
    guardModelOutput(modelOutput({ factIds: ["unknown"], sourceIds: ["fake"] }), {
      confirmedFactIds: new Set(["f1"]),
      sourceIds: new Set(["s1"]),
    }),
  ).toThrow("MODEL_REFERENCE_INVALID");
});

it("aborts a fast request after eight seconds", async () => {
  vi.useFakeTimers();
  const request = adapter.completeStructured(slowRequest({ timeoutMs: 8_000 }));
  await vi.advanceTimersByTimeAsync(8_001);
  await expect(request).rejects.toThrow("MODEL_TIMEOUT");
});
```

- [ ] **Step 2: Verify failure**

Run: `pnpm vitest run tests/unit/ai tests/integration/ai/model-adapter.test.ts`
Expected: FAIL because adapters and guards are absent.

- [ ] **Step 3: Implement adapters**

Send OpenAI-compatible `/chat/completions` requests with `response_format: { type: "json_object" }`, include the Zod-derived output contract in the system instruction, then validate the returned JSON locally. Use an `AbortController`, no request-body logging, and a request-level timeout. The concurrency limiter queues only model calls up to a configurable maximum; it is not a global product lock.

The mock adapter returns fixture-tagged output:

```ts
return {
  data: fixture,
  provenance: { provider: "mock", model: "fixture-v1", realModel: false },
};
```

UI and telemetry must preserve this provenance.

- [ ] **Step 4: Verify adapter boundaries**

Run: `pnpm vitest run tests/unit/ai tests/integration/ai/model-adapter.test.ts`
Expected: PASS for valid schema, timeout, abort, concurrency cap, invalid references, and mock provenance.

- [ ] **Step 5: Commit**

```bash
git add src/server/ai tests/unit/ai tests/integration/ai
git commit -m "feat(ai): add guarded structured model adapter"
```

---

### Task 10: Progressive Analysis Orchestrator

**Files:**
- Create: `src/modules/analysis/analysis-repository.ts`
- Create: `src/modules/analysis/analysis-service.ts`
- Create: `src/modules/analysis/analysis-runner.ts`
- Create: `src/modules/analysis/enrichment.ts`
- Create: `src/server/runtime/clock.ts`
- Test: `tests/unit/analysis/analysis-runner.test.ts`
- Test: `tests/integration/analysis/progressive-analysis.test.ts`

**Interfaces:**
- Consumes: gap engine, corpus repository, material repository, analysis repository, model adapter, plan engine.
- Produces:
  - `AnalysisService.start(command): Promise<{ analysisId; requestId; reused }>`
  - `AnalysisRunner.runFast(analysisId): Promise<void>`
  - `AnalysisRunner.runEnrichment(analysisId): Promise<void>`

- [ ] **Step 1: Write deadline and stale-write tests**

```ts
it("persists deterministic fast insight before the 12-second server deadline", async () => {
  const clock = fakeClock();
  model.delayForever();
  const run = runner.runFast("analysis-1");
  await clock.advance(12_000);
  await run;
  expect(repository.stage("analysis-1")).toBe("fast_insight_ready");
  expect(repository.payload("analysis-1").gaps).toHaveLength(3);
});

it("does not activate a late result for an old input version", async () => {
  await runner.runFast("analysis-v1");
  expect(await repository.currentFor(sessionId)).toBe("analysis-v2");
});
```

- [ ] **Step 2: Verify failure**

Run: `pnpm vitest run tests/unit/analysis/analysis-runner.test.ts tests/integration/analysis/progressive-analysis.test.ts`
Expected: FAIL because the orchestrator is missing.

- [ ] **Step 3: Implement two-stage orchestration**

Start deterministic matching and the optional model request concurrently. Race the model against 8 seconds, merge only guarded model explanations, then transact `fast_insight_ready` no later than the 12-second server deadline. Run enrichment as a separate persisted stage and preserve fast results on failure.

Before every write:

```ts
if (!(await repository.matchesInputVersion(analysisId, inputVersion))) {
  await repository.markHistorical(analysisId);
  return;
}
```

Reuse an existing analysis for the same `(sessionId, idempotencyKey)`.

- [ ] **Step 4: Verify progressive invariants**

Run: `pnpm vitest run tests/unit/analysis tests/integration/analysis`
Expected: PASS for model success, timeout, enrichment failure, idempotency, stale input, and fast-result preservation.

- [ ] **Step 5: Commit**

```bash
git add src/modules/analysis src/server/runtime/clock.ts tests/unit/analysis tests/integration/analysis
git commit -m "feat(analysis): orchestrate progressive gap results"
```

---

### Task 11: Analysis HTTP, Polling, and SSE

**Files:**
- Create: `src/server/http/require-session.ts`
- Create: `src/server/runtime/container.ts`
- Create: `src/app/api/analyses/route.ts`
- Create: `src/app/api/analyses/[analysisId]/route.ts`
- Create: `src/app/api/analyses/[analysisId]/events/route.ts`
- Test: `tests/integration/api/analysis-routes.test.ts`
- Test: `tests/integration/api/analysis-events.test.ts`

**Interfaces:**
- Consumes: `AnalysisService`, `AnalysisRepository`.
- Produces:
  - `POST /api/analyses`
  - `GET /api/analyses/:analysisId`
  - `GET /api/analyses/:analysisId/events?after=<sequence>`

- [ ] **Step 1: Write API event tests**

```ts
it("returns the existing analysis for a repeated idempotency key", async () => {
  const first = await postAnalysis({ idempotencyKey: "one" });
  const second = await postAnalysis({ idempotencyKey: "one" });
  expect(second.analysisId).toBe(first.analysisId);
  expect(second.reused).toBe(true);
});

it("resumes events after the requested sequence", async () => {
  const response = await getEvents("a1", { after: 2 });
  expect(parseSse(response).every((event) => event.sequence > 2)).toBe(true);
});
```

- [ ] **Step 2: Verify failure**

Run: `pnpm vitest run tests/integration/api/analysis-routes.test.ts tests/integration/api/analysis-events.test.ts`
Expected: FAIL because HTTP composition is absent.

- [ ] **Step 3: Implement route handlers**

`POST` validates the current confirmed input version and returns `202`. `GET` returns persisted state for polling. The event route uses a `ReadableStream`, sends numbered SSE events, heartbeats every 15 seconds after the fast deadline, and closes on terminal state. It never creates an analysis.

- [ ] **Step 4: Verify HTTP recovery**

Run: `pnpm vitest run tests/integration/api/analysis-routes.test.ts tests/integration/api/analysis-events.test.ts`
Expected: PASS for unauthorized access, idempotency, current-version enforcement, polling, SSE resume, and terminal close.

- [ ] **Step 5: Commit**

```bash
git add src/server/http src/server/runtime/container.ts src/app/api/analyses tests/integration/api/analysis-routes.test.ts tests/integration/api/analysis-events.test.ts
git commit -m "feat(api): expose resilient progressive analysis"
```

---

### Task 12: Visual System, Landing, and Invite Experience

**Files:**
- Create: `src/components/ui/button.tsx`
- Create: `src/components/ui/panel.tsx`
- Create: `src/components/ui/status-chip.tsx`
- Create: `src/components/ui/field.tsx`
- Create: `src/components/ui/progress-stage.tsx`
- Create: `src/components/invite/invite-form.tsx`
- Create: `src/app/invite/page.tsx`
- Modify: `src/app/page.tsx`
- Modify: `src/app/globals.css`
- Test: `tests/unit/components/invite-form.test.tsx`

**Interfaces:**
- Consumes: `POST /api/beta/sessions`.
- Produces: reusable accessible UI primitives and invite flow.

- [ ] **Step 1: Write invite interaction test**

```tsx
// @vitest-environment jsdom
it("shows the recovery code once after a valid invite", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ recoveryCode: "EJT-ONE-TIME" }), { status: 201 }),
    ),
  );
  render(<InviteForm />);
  await userEvent.type(screen.getByLabelText("邀请码"), "BETA-2026");
  await userEvent.click(screen.getByRole("button", { name: "进入工作台" }));
  expect(await screen.findByText("EJT-ONE-TIME")).toBeInTheDocument();
  expect(screen.getByText("恢复码只展示这一次")).toBeInTheDocument();
});
```

- [ ] **Step 2: Verify failure**

Run: `pnpm vitest run tests/unit/components/invite-form.test.tsx`
Expected: FAIL because the design system and form do not exist.

- [ ] **Step 3: Implement the visual foundation**

Use a restrained editorial-workbench aesthetic:

- warm off-white canvas;
- ink/navy primary text;
- cobalt action color;
- coral reserved for P0;
- serif display face only for the main promise, sans-serif for product UI;
- 8 px spacing grid, 12–20 px radii, thin borders, no glassmorphism;
- visible focus rings and reduced-motion support.

Landing copy must lead with the gap-closure promise rather than “AI resume optimization.” Build semantic controls and a single primary action.

- [ ] **Step 4: Verify UI foundation**

Run: `pnpm vitest run tests/unit/components/invite-form.test.tsx && pnpm typecheck && pnpm lint`
Expected: PASS with keyboard labels, one-time recovery warning, and no type/lint errors.

- [ ] **Step 5: Commit**

```bash
git add src/components/ui src/components/invite src/app/invite src/app/page.tsx src/app/globals.css tests/unit/components/invite-form.test.tsx
git commit -m "feat(ui): establish trusted invite experience"
```

---

### Task 13: Material Intake and Confirmation UI

**Files:**
- Create: `src/components/materials/material-intake.tsx`
- Create: `src/components/materials/document-dropzone.tsx`
- Create: `src/components/materials/confirmation-editor.tsx`
- Create: `src/components/materials/fact-status-list.tsx`
- Create: `src/app/workspace/materials/page.tsx`
- Test: `tests/unit/components/material-intake.test.tsx`
- Test: `tests/e2e/materials.spec.ts`

**Interfaces:**
- Consumes: material upload and confirmation APIs.
- Produces: confirmed material set and navigation to analysis.

- [ ] **Step 1: Write fallback interaction test**

```tsx
// @vitest-environment jsdom
it("preserves the JD and offers paste fallback after a resume parse failure", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ code: "DOCUMENT_PARSE_FAILED" }), { status: 422 }),
    ),
  );
  render(<MaterialIntake />);
  await userEvent.type(screen.getByLabelText("目标岗位 JD"), "负责 Agent 产品");
  await uploadResume(screen, corruptPdf);
  expect(await screen.findByText("无法读取这份文件")).toBeInTheDocument();
  expect(screen.getByLabelText("目标岗位 JD")).toHaveValue("负责 Agent 产品");
  expect(screen.getByRole("button", { name: "改为粘贴简历文本" })).toBeVisible();
});
```

- [ ] **Step 2: Verify failure**

Run: `pnpm vitest run tests/unit/components/material-intake.test.tsx`
Expected: FAIL because intake components are absent.

- [ ] **Step 3: Implement intake and confirmation**

Provide separate JD and resume regions, clear file limits, parse state, editable normalized text, and fact statuses. Disable analysis until both materials and candidate facts are explicitly confirmed. Changing confirmed content after analysis must warn that a new input version will supersede the current result.

- [ ] **Step 4: Verify materials**

Run: `pnpm vitest run tests/unit/components/material-intake.test.tsx && pnpm playwright test tests/e2e/materials.spec.ts`
Expected: PASS for paste, PDF, DOCX, parse fallback, keyboard use, confirmation, and version warning.

- [ ] **Step 5: Commit**

```bash
git add src/components/materials src/app/workspace/materials tests/unit/components/material-intake.test.tsx tests/e2e/materials.spec.ts
git commit -m "feat(ui): add material confirmation workflow"
```

---

### Task 14: Progressive Gap Workspace

**Files:**
- Create: `src/components/analysis/use-progressive-analysis.ts`
- Create: `src/components/analysis/analysis-workspace.tsx`
- Create: `src/components/analysis/overall-judgment.tsx`
- Create: `src/components/analysis/gap-card.tsx`
- Create: `src/components/analysis/evidence-drawer.tsx`
- Create: `src/components/analysis/source-signal.tsx`
- Create: `src/app/workspace/analysis/page.tsx`
- Create: `tests/unit/components/fakes/progressive-transport.ts`
- Test: `tests/unit/components/progressive-analysis.test.tsx`
- Test: `tests/e2e/progressive-analysis.spec.ts`

**Interfaces:**
- Consumes: analysis POST/status/SSE APIs.
- Produces: current-version gap workspace, recovery-aware client hook, and a test transport exposing `failSse()`, `respondToPoll(payload)`, and `emitSse(event)`.

- [ ] **Step 1: Write stream-fallback and stale-event tests**

```tsx
// @vitest-environment jsdom
it("polls persisted state when SSE fails and ignores a stale input version", async () => {
  const transport = createProgressiveTransportFake();
  const { result } = renderHook(() =>
    useProgressiveAnalysis({ analysisId: "a2", inputVersion: "v2", transport }),
  );
  transport.failSse();
  transport.respondToPoll(fastInsight({ inputVersion: "v2" }));
  transport.emitSse(fastInsightEvent({ inputVersion: "v1" }));
  await waitFor(() => expect(result.current.stage).toBe("fast_insight_ready"));
  expect(result.current.inputVersion).toBe("v2");
});
```

- [ ] **Step 2: Verify failure**

Run: `pnpm vitest run tests/unit/components/progressive-analysis.test.tsx`
Expected: FAIL because the hook and workspace do not exist.

- [ ] **Step 3: Implement progressive rendering**

Show actual named stages, never a fabricated percentage. Once fast insight arrives, render exactly three gap cards with priority text plus icon, impact reason, source confidence, and next action. Preserve those cards when enrichment fails. Show mock provenance as “演示数据” and old input versions as “基于旧材料”.

- [ ] **Step 4: Verify progressive UX**

Run: `pnpm vitest run tests/unit/components/progressive-analysis.test.tsx && pnpm playwright test tests/e2e/progressive-analysis.spec.ts`
Expected: PASS for normal stream, SSE failure with polling, model timeout, enrichment failure, refresh recovery, and stale-event rejection.

- [ ] **Step 5: Commit**

```bash
git add src/components/analysis src/app/workspace/analysis tests/unit/components/progressive-analysis.test.tsx tests/e2e/progressive-analysis.spec.ts
git commit -m "feat(ui): render progressive evidence-backed gaps"
```

---

### Task 15: Plan, Practice, and Retest Workflow

**Files:**
- Create: `src/app/api/plans/[planId]/route.ts`
- Create: `src/app/api/tasks/[taskId]/complete/route.ts`
- Create: `src/app/api/practice/[questionId]/attempts/route.ts`
- Create: `src/components/plan/time-budget.tsx`
- Create: `src/components/plan/seven-day-plan.tsx`
- Create: `src/components/plan/task-card.tsx`
- Create: `src/components/practice/practice-question.tsx`
- Create: `src/components/practice/retest-result.tsx`
- Create: `src/app/workspace/plan/page.tsx`
- Create: `src/app/workspace/practice/page.tsx`
- Test: `tests/integration/api/plan-practice-routes.test.ts`
- Test: `tests/e2e/plan-retest.spec.ts`

**Interfaces:**
- Consumes: plan and practice repositories/engines.
- Produces: task completion and retest state without fact mutation.

- [ ] **Step 1: Write end-to-end domain boundary test**

```ts
it("updates readiness after a passed retest without creating a confirmed fact", async () => {
  const before = await getFacts(sessionId);
  await completeTask(taskId, deliverableText);
  await submitAttempt(questionId, strongAnswer);
  const after = await getFacts(sessionId);
  expect(after).toEqual(before);
  expect((await getRetest(taskId)).readinessDelta).toBeGreaterThan(0);
});
```

- [ ] **Step 2: Verify failure**

Run: `pnpm vitest run tests/integration/api/plan-practice-routes.test.ts`
Expected: FAIL because plan/practice routes are absent.

- [ ] **Step 3: Implement the workflow**

Require a daily time selection before plan generation. Persist deliverables before returning success. Questions must include topic, JD requirement, source event IDs, and rubric. If a source becomes unavailable, show the last verification state and keep the reference.

- [ ] **Step 4: Verify workflow**

Run: `pnpm vitest run tests/integration/api/plan-practice-routes.test.ts && pnpm playwright test tests/e2e/plan-retest.spec.ts`
Expected: PASS from time selection through task completion, practice, retest, readiness update, refresh, and source-state display.

- [ ] **Step 5: Commit**

```bash
git add src/app/api/plans src/app/api/tasks src/app/api/practice src/components/plan src/components/practice src/app/workspace/plan src/app/workspace/practice tests/integration/api/plan-practice-routes.test.ts tests/e2e/plan-retest.spec.ts
git commit -m "feat(workflow): close the task and retest loop"
```

---

### Task 16: Privacy, Recovery, and Verifiable Deletion

**Files:**
- Create: `src/modules/session/deletion-service.ts`
- Create: `src/app/api/privacy/delete/route.ts`
- Create: `src/components/privacy/privacy-summary.tsx`
- Create: `src/components/privacy/recovery-panel.tsx`
- Create: `src/components/privacy/delete-session.tsx`
- Create: `src/app/workspace/privacy/page.tsx`
- Test: `tests/integration/privacy/deletion.test.ts`
- Test: `tests/e2e/privacy.spec.ts`

**Interfaces:**
- Consumes: all session-owned repositories.
- Produces:
  - `DeletionService.deleteAnalysis(sessionId, analysisId)`
  - `DeletionService.deleteSession(sessionId)`
  - `DELETE /api/privacy/delete`

- [ ] **Step 1: Write transaction and no-fake-success tests**

```ts
it("deletes all session business data and invalidates recovery in one transaction", async () => {
  await deletionService.deleteSession(sessionId);
  expect(await repository.countOwnedRows(sessionId)).toBe(0);
  await expect(sessionService.recover(recoveryCode)).rejects.toThrow("RECOVERY_INVALID");
});

it("returns failure when the transaction rolls back", async () => {
  repository.failNextDelete();
  const response = await deleteSessionRequest();
  expect(response.status).toBe(500);
  expect(response.body.deleted).toBe(false);
});
```

- [ ] **Step 2: Verify failure**

Run: `pnpm vitest run tests/integration/privacy/deletion.test.ts`
Expected: FAIL because deletion service is absent.

- [ ] **Step 3: Implement deletion and privacy UI**

Delete child records and the session in a database transaction, clear the cookie only after commit, and retain only aggregate metrics that have no session ID or content. The UI lists stored normalized data, model-sent fields, retention, recovery rotation, and the exact effect of deletion.

- [ ] **Step 4: Verify privacy behavior**

Run: `pnpm vitest run tests/integration/privacy/deletion.test.ts && pnpm playwright test tests/e2e/privacy.spec.ts`
Expected: PASS for analysis-only deletion, session deletion, rollback, cookie clearing, recovery invalidation, and truthful error UI.

- [ ] **Step 5: Commit**

```bash
git add src/modules/session/deletion-service.ts src/app/api/privacy src/components/privacy src/app/workspace/privacy tests/integration/privacy tests/e2e/privacy.spec.ts
git commit -m "feat(privacy): add recoverable sessions and verified deletion"
```

---

### Task 17: Telemetry and Controlled Performance Harness

**Files:**
- Create: `src/modules/telemetry/domain.ts`
- Create: `src/modules/telemetry/telemetry-service.ts`
- Create: `src/server/runtime/safe-logger.ts`
- Create: `scripts/performance/first-insight.ts`
- Test: `tests/unit/telemetry/safe-logger.test.ts`
- Test: `tests/integration/performance/first-insight.test.ts`

**Interfaces:**
- Consumes: analysis stage timestamps.
- Produces safe product events and command `pnpm perf:first-insight`.

- [ ] **Step 1: Write redaction and deadline tests**

```ts
it("removes resume, recovery, key, and model body fields from logs", () => {
  const entry = safeLog({
    resumeText: "private",
    recoveryCode: "secret",
    apiKey: "key",
    modelRequest: { messages: [] },
    analysisId: "a1",
  });
  expect(entry).toEqual({ analysisId: "a1" });
});

it("reports a failure when any controlled valid request exceeds 15 seconds", async () => {
  const report = summarizeDurations([2_100, 7_500, 15_001]);
  expect(report.passesHardMaximum).toBe(false);
});
```

- [ ] **Step 2: Verify failure**

Run: `pnpm vitest run tests/unit/telemetry tests/integration/performance/first-insight.test.ts`
Expected: FAIL because telemetry and performance summarization are absent.

- [ ] **Step 3: Implement minimal events and harness**

Record event name, timestamps, anonymous analysis identifiers, stage, duration, result state, and adapter provenance. Do not record input text. The harness runs normal, 8-second model timeout, and concurrent scenarios; it reports count, p50, p95, max, hard-maximum status, and the exact environment label.

- [ ] **Step 4: Verify metrics**

Run: `pnpm vitest run tests/unit/telemetry tests/integration/performance/first-insight.test.ts && pnpm perf:first-insight -- --adapter=mock --runs=30 --concurrency=3`
Expected: tests PASS and the controlled mock report has max `<= 15000`, p95 `<= 12000`, with adapter clearly labeled `mock`.

- [ ] **Step 5: Commit**

```bash
git add src/modules/telemetry src/server/runtime/safe-logger.ts scripts/performance tests/unit/telemetry tests/integration/performance package.json
git commit -m "test(perf): measure honest first-insight latency"
```

---

### Task 18: Full Browser, Accessibility, Visual, and Documentation Gate

**Files:**
- Create: `tests/e2e/full-flow.spec.ts`
- Create: `tests/e2e/stale-input.spec.ts`
- Create: `tests/e2e/reconnect.spec.ts`
- Create: `tests/e2e/accessibility.spec.ts`
- Create: `tests/e2e/responsive.spec.ts`
- Create: `tests/e2e/visual.spec.ts`
- Create: `tests/e2e/helpers.ts`
- Create: `docs/acceptance/screenshots/.gitkeep`
- Create: `docs/acceptance/2026-07-30-local-mvp.md`
- Create: `docs/content-evaluation/README.md`
- Create: `README.md`
- Modify: `task_plan.md`
- Modify: `notes.md`

**Interfaces:**
- Consumes: the complete local MVP.
- Produces: repeatable acceptance commands, screenshots, evidence boundaries, and handoff documentation.

- [ ] **Step 1: Write full-flow and accessibility tests**

```ts
test("completes the gap-closure loop", async ({ page }) => {
  await enterBeta(page);
  await confirmMaterials(page);
  await startAnalysis(page);
  await expect(page.getByTestId("top-gap")).toHaveCount(3, { timeout: 15_000 });
  await generatePlan(page, 30);
  await completeFirstTask(page);
  await submitPractice(page);
  await expect(page.getByText("准备状态已更新")).toBeVisible();
});

test("has no automatically detectable WCAG A/AA violations", async ({ page }) => {
  await page.goto("/");
  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
    .analyze();
  expect(results.violations).toEqual([]);
});
```

Define `enterBeta`, `confirmMaterials`, `startAnalysis`, `generatePlan`, `completeFirstTask`, and `submitPractice` in `tests/e2e/helpers.ts` using role-based Playwright locators. `visual.spec.ts` captures deterministic desktop `1440x1000` and mobile `390x844` screenshots of landing, material confirmation, fast insight, and seven-day plan into `docs/acceptance/screenshots/`; disable animation and use the mock adapter plus demo snapshot for repeatability.

- [ ] **Step 2: Run the complete suite and capture failures**

Run: `pnpm test:unit && pnpm test:integration && pnpm test:e2e && pnpm typecheck && pnpm lint && pnpm build`
Expected: any uncovered wiring or visual issue fails before acceptance is written.

- [ ] **Step 3: Fix only evidence-backed failures and write handoff docs**

README must identify:

- local MVP status;
- demo snapshot and mock-model labels;
- real-model environment variables without values;
- install, migrate, seed, dev, test, and performance commands;
- raw-file deletion and normalized-data retention;
- unsupported features and known limitations;
- distinction between engineering completion and 8–15 user product validation.

The acceptance document records exact commands, commit, browser, viewport, adapter, snapshot ID, test counts, performance report path, screenshots, and unresolved manual content review.

- [ ] **Step 4: Re-run the authoritative verification**

Run:

```bash
pnpm db:migrate
pnpm test:unit
pnpm test:integration
pnpm test:e2e
pnpm typecheck
pnpm lint
pnpm build
pnpm perf:first-insight -- --adapter=mock --runs=30 --concurrency=3
git diff --check
git status --short
```

Expected: all code/test commands PASS; performance meets the controlled mock contract; `git diff --check` is empty; only intended acceptance documentation is uncommitted before the final commit.

- [ ] **Step 5: Commit**

```bash
git add tests/e2e docs/acceptance docs/content-evaluation README.md task_plan.md notes.md
git commit -m "docs(release): verify local gap-closure MVP"
```

---

## Spec Coverage Matrix

| Specification requirement | Implementation task |
|---|---|
| Single web workspace and invite | Tasks 1, 12 |
| Confirmed facts only | Tasks 3, 8, 9, 15 |
| Explainable P0/P1/P2 and overall judgment | Task 4 |
| Three real gaps by 15 seconds | Tasks 10, 11, 14, 17 |
| SSE plus polling recovery | Tasks 11, 14 |
| Input/request/analysis version isolation | Tasks 3, 6, 10, 11, 14 |
| Seven-day capacity, task deliverable, retest | Tasks 5, 15 |
| Practice cannot become experience | Tasks 3, 5, 15 |
| Anonymous invite, recovery rotation | Tasks 7, 16 |
| Raw file deletion | Task 8 |
| Safe logs and model boundaries | Tasks 9, 17 |
| Versioned offline corpus | Task 2 plus the separate corpus plan |
| Privacy and verifiable deletion | Task 16 |
| Responsive, accessible visual system | Tasks 12–15, 18 |
| Unit, integration, E2E, performance gates | Tasks 1–18 |
| Honest release and validation boundaries | Task 18 |

## Execution Order

Execute Tasks 1–11 in order because they establish contracts and adapters. The corpus pipeline can run after Task 2 because it targets the same snapshot schema. Execute Tasks 12–16 after the API contracts stabilize. Finish with Tasks 17–18 and do not claim real-model latency or product value from mock and automated evidence.
