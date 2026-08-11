# Easy Job Tutor Web Public Beta Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** In one delivery week, turn the existing Easy Job Tutor Web prototype into a publicly accessible Chinese Beta whose single-JD resume-tailoring flow is truthful, privacy-safe, mobile-usable, testable, observable, and reversible.

**Architecture:** Keep the existing Vue 3 global-build frontend and FastAPI/Vercel deployment to avoid a framework migration during the launch week. Split backend validation, evidence matching, errors, and telemetry into focused modules; expose a versioned `/api/v1/analyses` contract; make the frontend consume only that contract. Treat keyword coverage as an explainable evidence signal rather than employability, ATS, credibility, or interview scoring.

**Tech Stack:** Python 3.12, FastAPI 0.141.1, Vue 3 pinned global production build, plain HTML/CSS/JavaScript, Vercel Python functions/static hosting, `unittest`, Playwright 1.55.0, GitHub Actions.

## Global Constraints

- Preserve all pre-existing uncommitted user work in `README.md`, `api/matcher.py`, `app.js`, `index.html`, `styles.css`, `tests/test_matcher.py`, `project-review-notes.md`, `project-review-plan.md`, and `resume-project-deliverable.md`; never reset, overwrite, discard, or accidentally bundle it.
- Public Beta scope is one JD + one resume → requirement extraction → evidence status → fact-safe rewrite → user decision → Markdown export.
- Hide multi-JD comparison, learning path, mock interview, English mode, accounts, OCR, payments, and unvalidated five-dimension scores from the public flow.
- Supported resume types are PDF, DOCX, and TXT only; maximum upload size is 5 MiB; PDF maximum is 10 pages; legacy `.doc` is not supported.
- JD length is 50–20,000 Unicode characters after trimming.
- Raw JD text, resume text, evidence text, filenames, suggestions, names, emails, and phone numbers must never enter analytics or application logs.
- Every result carries `algorithm_version` and `knowledge_base_version`.
- A negative statement such as “I have no Python experience” must never become positive evidence.
- A skills-only keyword list without project/action context is `uncertain`, not `evidenced`.
- New numbers, responsibilities, ownership, tools, and outcomes remain `pending_confirmation` and are excluded from default export.
- Mobile acceptance viewport is 390×844 with no page-level horizontal scrolling.
- Application timeout is 20 seconds; frontend timeout is 22 seconds.
- The production Beta must use correct 4xx/5xx status codes, request IDs, health checks, privacy-safe telemetry, monitoring, and a tested rollback path.
- Development agents do not approve their own task; every task requires a fresh reviewer and fresh command output.
- Tests are written before production code for every behavior change.

## Preflight: Protect Existing Work

The current checkout contains user-owned uncommitted work. Before Task 1, the coordinator agent must:

```bash
git status --short
git diff -- README.md api/matcher.py app.js index.html styles.css
sed -n '1,320p' tests/test_matcher.py
```

Record which current hunks belong to JD-targeted matching and resume optimization. Execute the plan in the current checkout unless the product owner first creates a reviewed checkpoint commit containing those hunks. Do not create an isolated worktree from `HEAD` and silently lose the WIP.

Every commit command below is a file allowlist, not permission to stage pre-existing hunks. First run `git add -N tests/test_matcher.py` so the untracked test can be patch-staged without adding its contents. For the dirty paths recorded above, stage interactively with `git add -p -- README.md api/matcher.py app.js index.html styles.css tests/test_matcher.py`, inspect those paths with `git diff --cached`, and include only the current task's hunks. Keep the three pre-existing review documents untracked. If an old and new change occupy one inseparable hunk, leave that path unstaged and ask the product owner to approve a WIP checkpoint commit; never hide the overlap inside a task commit. Before every commit, run `git diff --cached --name-only` and `git diff --cached`.

## File Structure and Ownership

### Existing files retained

- `api/main.py`: FastAPI app factory and HTTP orchestration only.
- `api/parser.py`: bytes-to-text parsing with resource limits.
- `api/matcher.py`: requirement selection, coverage aggregation, and rewrite orchestration.
- `api/knowledge.py`: role knowledge base and versions.
- `index.html`: public Beta DOM and static legal links.
- `app.js`: Vue state, API client, review decisions, export, and safe event calls.
- `styles.css`: responsive, accessible Beta UI.
- `vercel.json`: security headers and Vercel routing configuration.

### New focused files

- `api/config.py`: immutable limits and public version constants.
- `api/errors.py`: `ApiError`, request ID middleware, and JSON error handlers.
- `api/validation.py`: JD and upload validation before parser execution.
- `api/evidence.py`: boundary-aware, negation-aware evidence classification.
- `api/telemetry.py`: allowlisted, body-free structured events.
- `privacy.html`: Chinese privacy processing notice.
- `terms.html`: Chinese Beta usage terms and capability limits.
- `vendor/vue.global.prod.js`: pinned Vue global runtime served from the same origin.
- `vendor/VUE-LICENSE.txt`: Vue license notice for the vendored asset.
- `dev-requirements.txt`: test-only Python dependencies.
- `package.json` and `package-lock.json`: pinned browser-test dependencies.
- `playwright.config.js`: local FastAPI web server and device projects.
- `e2e/public-beta.spec.js`: public Beta happy path, mobile, errors, consent, and export.
- `tests/test_validation.py`: JD/file limit tests.
- `tests/test_evidence.py`: negation, boundaries, context, and status tests.
- `tests/test_api_contract.py`: versioned API and HTTP error contract tests.
- `tests/test_telemetry.py`: PII/field allowlist tests.
- `tests/test_evaluator.py`: frozen-set schema and metric calculation tests.
- `tests/fixtures/resume.txt`: synthetic non-sensitive resume.
- `tests/fixtures/jd.txt`: synthetic non-sensitive JD.
- `evals/public_beta_cases.jsonl`: 150 fixed evidence and rewrite quality cases.
- `.github/workflows/ci.yml`: Python, JavaScript syntax, and Playwright gates.
- `scripts/evaluate_public_beta.py`: deterministic quality-set runner and metric reporter.
- `scripts/smoke_public_beta.py`: health and synthetic end-to-end production smoke test.
- `docs/runbooks/public-beta-release.md`: release, monitoring, rollback, and incident steps.
- `docs/metrics/public-beta-events.md`: event dictionary and metric equations.
- `docs/quality/public-beta-evaluation.md`: case ownership, review status, and quality acceptance record.

## Dependency Waves

- Wave 0, serial: Task 1.
- Wave 1, parallel after Task 1: Tasks 2, 3, and 4. Task 2 owns public copy/legal files; Task 3 owns backend contracts; Task 4 owns parser limits.
- Wave 2, serial: Tasks 5 and 6 because both establish the result schema.
- Wave 3, serial on shared frontend files: Tasks 7 then 8.
- Wave 4, parallel after Tasks 6 and 8: Tasks 9, 10, and 11.
- Wave 5, serial: Tasks 12 and 13.

## Requirement Traceability

| Approved requirement | Implementation tasks | Release evidence |
|---|---|---|
| FR-01 JD input limits | 3, 6 | validation and contract tests |
| FR-02, FR-03, FR-04, FR-05 upload, true type, consent, parser failures | 2, 3, 4 | validation/parser tests and E2E |
| FR-06, FR-07, FR-08 JD evidence, resume evidence, uncertainty | 5, 6, 10 | evidence tests and frozen quality report |
| FR-09 fact-safe rewrites | 6, 10 | fabricated fact metric |
| FR-10, FR-11, FR-12 user decisions, export, feedback | 8, 9 | happy-path E2E and safe event sample |
| FR-13 Chinese-only public promise | 2 | public navigation/copy E2E |
| FR-14 responsive core flow | 7, 13 | 390×844 Playwright and device spot checks |
| NFR-01 availability | 9, 12, 13 | health/alert proof and gray metrics |
| NFR-02 performance | 11, 13 | local regression plus production p95 |
| NFR-03 capacity/fail-fast | 3, 4, 11 | limit, saturation, 429, and 504 tests |
| NFR-04, NFR-05, NFR-06 accessibility, responsive, compatibility | 7, 13 | keyboard/mobile E2E and browser matrix |
| NFR-07 observability | 9 | request ID, safe events, saved views, alert drill |
| NFR-08 rollback | 12, 13 | timed rollback drill |
| NFR-09 reproducibility | 1 | pinned runtime/dependencies and CI |

---

### Task 1: Reproducible Test and CI Foundation

**Day:** 1

**Files:**
- Create: `dev-requirements.txt`
- Create: `package.json`
- Create: `package-lock.json`
- Create: `playwright.config.js`
- Create: `.github/workflows/ci.yml`
- Modify: `.gitignore`
- Modify: `README.md`
- Test: existing `tests/test_parser.py`
- Test: existing `tests/test_matcher.py`

**Interfaces:**
- Consumes: Python 3.12 declared by `.python-version`; current `unittest` suite.
- Produces: `python -m unittest discover -s tests -v`, `npm run check`, and `npm run test:e2e` as the only accepted verification entry points for later tasks.

- [ ] **Step 1: Add exact development dependencies**

Create the test/config directories first:

```bash
mkdir -p e2e .github/workflows
```

Create `dev-requirements.txt`:

```text
-r requirements.txt
httpx==0.28.1
```

Create `package.json`:

```json
{
  "name": "easy-job-tutor-web",
  "private": true,
  "scripts": {
    "check": "node --check app.js && node --check playwright.config.js",
    "test:e2e": "playwright test"
  },
  "devDependencies": {
    "@playwright/test": "1.55.0"
  }
}
```

Run `npm install --package-lock-only` to generate and commit the lockfile.

- [ ] **Step 2: Write the browser-test server configuration**

Create `playwright.config.js`:

```javascript
const { defineConfig, devices } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  retries: 1,
  use: { baseURL: "http://127.0.0.1:8000", trace: "retain-on-failure" },
  webServer: {
    command: "python -m uvicorn api.main:app --host 127.0.0.1 --port 8000",
    url: "http://127.0.0.1:8000/api/health",
    reuseExistingServer: true,
    timeout: 30_000
  },
  projects: [
    { name: "desktop-chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile-390", use: { viewport: { width: 390, height: 844 } } }
  ]
});
```

- [ ] **Step 3: Add CI before adding new behavior**

Create `.github/workflows/ci.yml`:

```yaml
name: ci
on:
  pull_request:
  push:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - run: python -m pip install -r dev-requirements.txt
      - run: python -m unittest discover -s tests -v
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: npm
      - run: npm ci
      - run: npm run check
      - run: npx playwright install --with-deps chromium
      - run: npm run test:e2e
```

- [ ] **Step 4: Add an initial E2E placeholder-free health test**

Create `e2e/public-beta.spec.js` with a test that already applies to the current product:

```javascript
const { test, expect } = require("@playwright/test");

test("health endpoint returns ok", async ({ request }) => {
  const response = await request.get("/api/health");
  expect(response.status()).toBe(200);
  const body = await response.json();
  expect(body).toEqual({ status: "ok" });
});
```

- [ ] **Step 5: Run the full baseline and record real failures**

Run:

```bash
python -m unittest discover -s tests -v
npm ci
npm run check
npx playwright install chromium
npm run test:e2e
```

Expected: Python tests and health E2E pass in a fresh Python 3.12 environment. If pre-existing WIP tests fail, stop and report the exact failure; do not weaken or delete them.

- [ ] **Step 6: Commit only foundation files**

```bash
git add dev-requirements.txt package.json package-lock.json playwright.config.js .github/workflows/ci.yml e2e/public-beta.spec.js .gitignore README.md
git commit -m "test: add reproducible public beta CI"
```

---

### Task 2: Truthful Public Scope, Privacy Notice, and Terms

**Day:** 1–2

**Files:**
- Create: `privacy.html`
- Create: `terms.html`
- Create: `vendor/vue.global.prod.js`
- Create: `vendor/VUE-LICENSE.txt`
- Modify: `index.html`
- Modify: `app.js`
- Modify: `README.md`
- Test: `e2e/public-beta.spec.js`

**Interfaces:**
- Consumes: current Vue global frontend and current fact-safe rewrite WIP.
- Produces: same-origin Vue runtime, public Beta copy, privacy consent element `#privacy-consent`, and static `/privacy.html` and `/terms.html` links used by Task 8.

- [ ] **Step 1: Add failing public-copy and consent tests**

Append to `e2e/public-beta.spec.js`:

```javascript
test("public beta states its limits and requires privacy consent", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("公开 Beta")).toBeVisible();
  await expect(page.getByText("不预测录用结果")).toBeVisible();
  const consent = page.locator("#privacy-consent");
  await expect(consent).not.toBeChecked();
  await expect(page.getByRole("button", { name: "分析这份简历" })).toBeDisabled();
  await expect(page.getByRole("link", { name: "隐私说明" })).toHaveAttribute("href", "/privacy.html");
});

test("public navigation hides deferred features", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("多 JD 对比")).toHaveCount(0);
  await expect(page.getByText("学习路线")).toHaveCount(0);
  await expect(page.getByText("模拟面试")).toHaveCount(0);
  await expect(page.getByRole("button", { name: "EN" })).toHaveCount(0);
});
```

- [ ] **Step 2: Run the tests and verify they fail**

Run: `npm run test:e2e -- --grep "public beta|public navigation"`

Expected: FAIL because the current public copy, consent control, and reduced navigation do not exist.

- [ ] **Step 3: Vendor the exact Vue runtime**

Download the exact public file and license:

```bash
mkdir -p vendor
curl -fL https://unpkg.com/vue@3.5.18/dist/vue.global.prod.js -o vendor/vue.global.prod.js
curl -fL https://raw.githubusercontent.com/vuejs/core/v3.5.18/LICENSE -o vendor/VUE-LICENSE.txt
```

Change `index.html` from the floating `vue@3` URL to:

```html
<script src="/vendor/vue.global.prod.js"></script>
```

- [ ] **Step 4: Add truthful Beta copy and consent**

The rendered homepage must include these exact statements:

```html
<span class="beta-badge">公开 Beta</span>
<p class="capability-limit">本工具提供 JD 关键词覆盖与简历原文证据辅助，不预测录用结果，也不代表招聘方或 ATS 评分。</p>
<label class="consent-row" for="privacy-consent">
  <input id="privacy-consent" type="checkbox" v-model="privacyConsent" />
  <span>我已阅读并同意 <a href="/privacy.html" target="_blank" rel="noopener">隐私说明</a> 与 <a href="/terms.html" target="_blank" rel="noopener">使用条款</a></span>
</label>
```

Change the primary CTA text to `分析这份简历`. Remove or `v-if="false"` all public entries for multi-JD, learning path, mock interview, and locale switching; deleting dead public markup is preferred.

- [ ] **Step 5: Add legal pages with actual processing facts**

`privacy.html` must state in Chinese:

- PDF/DOCX/TXT is sent to the site’s Vercel-hosted server function for in-request parsing;
- the application does not call an external large-model API in this Beta;
- raw files and extracted text are not intentionally persisted by application code;
- operational infrastructure can process request metadata;
- application logs and analytics exclude filename, JD, resume, evidence, names, emails, and phone numbers;
- contact is the repository issue tracker: `https://github.com/yicLionel/Easy-Job-Tutor-Web/issues`;
- the user should avoid uploading information they are not authorized to process.

`terms.html` must state:

- output is assistance, not recruitment advice or a hiring decision;
- the user must confirm every pending fact;
- no outcome is guaranteed;
- prohibited abuse includes automated bulk upload, malicious files, and attempts to bypass limits;
- Beta may change or be withdrawn.

- [ ] **Step 6: Bind consent to submit eligibility**

In `app.js`, add:

```javascript
const PRIVACY_CONSENT_VERSION = "2026-08-11";
const privacyConsent = ref(false);
```

Update `canSubmit` so complete analysis requires `privacyConsent.value === true`. Append `privacy_consent_version` to `FormData`.

- [ ] **Step 7: Run tests and inspect copy**

Run:

```bash
npm run check
npm run test:e2e -- --grep "public beta|public navigation"
```

Expected: PASS. Manually search for inaccurate claims:

```bash
rg -n "录用概率|简历可信度|面试准备度|离线可用|无第三方上传|AI-powered" index.html app.js README.md privacy.html terms.html
```

Expected: no unsupported public claim; historical explanations in README must be rewritten, not merely hidden in the page.

- [ ] **Step 8: Commit**

```bash
git add index.html app.js README.md privacy.html terms.html vendor/vue.global.prod.js vendor/VUE-LICENSE.txt e2e/public-beta.spec.js
git commit -m "feat: define truthful public beta scope"
```

---

### Task 3: API Limits, Versions, and Structured Errors

**Day:** 2

**Files:**
- Create: `api/config.py`
- Create: `api/errors.py`
- Create: `api/validation.py`
- Create: `tests/test_validation.py`
- Modify: `api/main.py`
- Modify: `requirements.txt`
- Test: `tests/test_validation.py`

**Interfaces:**
- Produces: `validate_jd(text: str | None) -> str`, `validate_upload(filename: str, content_type: str | None, raw: bytes) -> ValidatedUpload`, and `ApiError(status_code, error_code, message, retryable=False, supported_action="")`.
- Consumed by: Tasks 4 and 6.

- [ ] **Step 1: Write failing limit and type tests**

Create `tests/test_validation.py`:

```python
import unittest
from api.errors import ApiError
from api.validation import validate_jd, validate_upload


class ValidationTests(unittest.TestCase):
    def test_jd_must_be_between_50_and_20000_characters(self):
        with self.assertRaisesRegex(ApiError, "至少 50"):
            validate_jd("Python developer")
        self.assertEqual(validate_jd("A" * 50), "A" * 50)
        with self.assertRaisesRegex(ApiError, "不能超过 20000"):
            validate_jd("A" * 20001)

    def test_upload_rejects_legacy_doc_and_files_over_5_mib(self):
        with self.assertRaisesRegex(ApiError, "PDF、DOCX 或 TXT"):
            validate_upload("resume.doc", "application/msword", b"doc")
        with self.assertRaisesRegex(ApiError, "5 MB"):
            validate_upload("resume.txt", "text/plain", b"x" * (5 * 1024 * 1024 + 1))

    def test_upload_rejects_fake_pdf_extension(self):
        with self.assertRaisesRegex(ApiError, "真实类型"):
            validate_upload("resume.pdf", "application/pdf", b"not-a-pdf")

    def test_upload_rejects_mime_mismatch(self):
        with self.assertRaisesRegex(ApiError, "MIME"):
            validate_upload("resume.pdf", "text/plain", b"%PDF-1.7")

    def test_upload_accepts_pdf_docx_and_txt_signatures(self):
        self.assertEqual(validate_upload("r.pdf", "application/pdf", b"%PDF-1.7").kind, "pdf")
        self.assertEqual(validate_upload("r.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", b"PK\x03\x04data").kind, "docx")
        self.assertEqual(validate_upload("r.txt", "text/plain", "简历".encode()).kind, "txt")
```

- [ ] **Step 2: Run tests to verify missing modules fail**

Run: `python -m unittest tests.test_validation -v`

Expected: ERROR importing `api.errors` or `api.validation`.

- [ ] **Step 3: Add immutable configuration**

Create `api/config.py`:

```python
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_PDF_PAGES = 10
MAX_DOCX_UNCOMPRESSED_BYTES = 20 * 1024 * 1024
MAX_DOCX_COMPRESSION_RATIO = 100
MIN_JD_CHARS = 50
MAX_JD_CHARS = 20_000
ANALYSIS_TIMEOUT_SECONDS = 20
ALGORITHM_VERSION = "evidence-v1"
KNOWLEDGE_BASE_VERSION = "2026-08-11"
PRIVACY_CONSENT_VERSION = "2026-08-11"
ALLOWED_ORIGINS = (
    "https://easy-job-tutor-web.vercel.app",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
)
```

- [ ] **Step 4: Add structured error type**

Create `api/errors.py`:

```python
from dataclasses import dataclass


@dataclass
class ApiError(Exception):
    status_code: int
    error_code: str
    message: str
    retryable: bool = False
    supported_action: str = ""

    def __str__(self) -> str:
        return self.message
```

- [ ] **Step 5: Implement minimal validation**

Create `api/validation.py` with this public shape:

```python
from dataclasses import dataclass
from pathlib import Path
from api.config import MAX_JD_CHARS, MAX_UPLOAD_BYTES, MIN_JD_CHARS
from api.errors import ApiError


@dataclass(frozen=True)
class ValidatedUpload:
    filename: str
    kind: str
    raw: bytes


def validate_jd(text: str | None) -> str:
    value = (text or "").strip()
    if len(value) < MIN_JD_CHARS:
        raise ApiError(400, "JD_TOO_SHORT", "岗位 JD 至少 50 个字符。", supported_action="请粘贴完整岗位描述。")
    if len(value) > MAX_JD_CHARS:
        raise ApiError(400, "JD_TOO_LONG", "岗位 JD 不能超过 20000 个字符。", supported_action="请删除无关页面内容后重试。")
    return value


def validate_upload(filename: str, content_type: str | None, raw: bytes) -> ValidatedUpload:
    if len(raw) > MAX_UPLOAD_BYTES:
        raise ApiError(413, "FILE_TOO_LARGE", "简历文件不能超过 5 MB。")
    suffix = Path(filename or "").suffix.lower()
    if suffix not in {".pdf", ".docx", ".txt"}:
        raise ApiError(415, "UNSUPPORTED_FILE_TYPE", "请上传 PDF、DOCX 或 TXT 文件。")
    allowed_mime = {
        ".pdf": {"application/pdf"},
        ".docx": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
        ".txt": {"text/plain"},
    }
    normalized_mime = (content_type or "").split(";", 1)[0].strip().lower()
    if normalized_mime and normalized_mime not in allowed_mime[suffix]:
        raise ApiError(415, "FILE_MIME_MISMATCH", "文件扩展名与 MIME 类型不一致。")
    signatures = {".pdf": raw.startswith(b"%PDF-"), ".docx": raw.startswith(b"PK\x03\x04"), ".txt": b"\x00" not in raw[:1024]}
    if not signatures[suffix]:
        raise ApiError(415, "FILE_SIGNATURE_MISMATCH", "文件扩展名与真实类型不一致。")
    return ValidatedUpload(filename=filename, kind=suffix[1:], raw=raw)
```

- [ ] **Step 6: Run tests**

Run: `python -m unittest tests.test_validation -v`

Expected: 5 tests PASS.

- [ ] **Step 7: Commit**

```bash
git add api/config.py api/errors.py api/validation.py tests/test_validation.py
git commit -m "feat: validate public beta inputs"
```

---

### Task 4: Parser Resource Limits and Explicit Failures

**Day:** 2–3

**Files:**
- Modify: `api/parser.py`
- Modify: `tests/test_parser.py`
- Consume: `api/config.py`, `api/errors.py`, `api/validation.py`

**Interfaces:**
- Consumes: `ValidatedUpload` from Task 3.
- Produces: `parse_validated_resume(upload: ValidatedUpload) -> str` and keeps `parse_resume(filename, bytes)` as a temporary compatibility wrapper.

- [ ] **Step 1: Write failing page, ZIP, and empty-text tests**

Add to `tests/test_parser.py` using mocks rather than large real files:

```python
from api.errors import ApiError
from api.validation import ValidatedUpload


def test_pdf_over_ten_pages_is_rejected(self):
    class _FakePdf:
        pages = [_FakePage("x")] * 11

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

    fake_pdf = _FakePdf()
    with patch("api.parser.pdfplumber.open", return_value=fake_pdf):
        with self.assertRaisesRegex(ApiError, "10 页"):
            parser.parse_validated_resume(ValidatedUpload("r.pdf", "pdf", b"%PDF-1.7"))

def test_empty_text_has_explicit_parse_error(self):
    with self.assertRaisesRegex(ApiError, "没有提取到可用文字"):
        parser.parse_validated_resume(ValidatedUpload("r.txt", "txt", b"   \n"))
```

Add DOCX tests that patch `zipfile.ZipFile.infolist()` with entries whose total uncompressed bytes exceed 20 MiB or whose compression ratio exceeds 100.

- [ ] **Step 2: Run tests and verify failure**

Run: `python -m unittest tests.test_parser -v`

Expected: FAIL because `parse_validated_resume` and limit errors do not exist.

- [ ] **Step 3: Add resource checks before extraction**

Implement these exact helpers in `api/parser.py`: `_validate_docx_archive(raw: bytes) -> None`, `_extract_pdf(raw: bytes, max_pages: int) -> str`, and `parse_validated_resume(upload: ValidatedUpload) -> str`.

`_validate_docx_archive` must sum `ZipInfo.file_size`, reject totals above `MAX_DOCX_UNCOMPRESSED_BYTES`, and reject any entry where `file_size / max(compress_size, 1) > MAX_DOCX_COMPRESSION_RATIO`.

`_extract_pdf` must inspect page count before extracting text and raise:

```python
ApiError(422, "PDF_TOO_MANY_PAGES", "PDF 简历不能超过 10 页。")
```

If extraction returns blank text, raise:

```python
ApiError(
    422,
    "RESUME_TEXT_EMPTY",
    "没有提取到可用文字。扫描件、加密文件或损坏文件暂不支持。",
    supported_action="请上传可复制文字的 PDF、DOCX 或 TXT。",
)
```

Do not catch `ApiError` inside general `except Exception` blocks.

- [ ] **Step 4: Keep one compatibility wrapper**

`parse_resume(filename, file_bytes)` may call `validate_upload` and `parse_validated_resume` so existing tests and entrypoints keep working during migration. It must no longer accept `.doc`.

- [ ] **Step 5: Run parser and full Python tests**

```bash
python -m unittest tests.test_parser -v
python -m unittest discover -s tests -v
```

Expected: all tests PASS.

- [ ] **Step 6: Commit**

```bash
git add api/parser.py tests/test_parser.py
git commit -m "feat: harden resume parsing limits"
```

---

### Task 5: Negation-Aware Evidence Engine

**Day:** 3

**Files:**
- Create: `api/evidence.py`
- Create: `tests/test_evidence.py`
- Modify: `api/matcher.py`
- Modify: `tests/test_matcher.py`

**Interfaces:**
- Produces: `classify_skill_evidence(skill: dict, resume_text: str) -> EvidenceMatch`.
- `EvidenceMatch.status` is one of `evidenced`, `uncertain`, `not_found`.
- Consumed by: Task 6 matcher response builder.

- [ ] **Step 1: Write the critical failing counterexamples**

Create `tests/test_evidence.py`:

```python
import unittest
from api.evidence import classify_skill_evidence


PYTHON = {"label": "Python", "keywords": ["python", "py"], "importance": 5, "dim": "核心技能"}


class EvidenceTests(unittest.TestCase):
    def test_explicit_negation_is_not_positive_evidence(self):
        match = classify_skill_evidence(PYTHON, "I have no Python experience and never used it in a project.")
        self.assertEqual(match.status, "not_found")
        self.assertEqual(match.reason, "explicit_negation")

    def test_keyword_list_without_action_context_is_uncertain(self):
        match = classify_skill_evidence(PYTHON, "Skills: Python, RAG, Agent")
        self.assertEqual(match.status, "uncertain")

    def test_project_action_with_keyword_is_evidenced(self):
        match = classify_skill_evidence(PYTHON, "项目经验：使用 Python 开发 FastAPI 服务并部署上线。")
        self.assertEqual(match.status, "evidenced")
        self.assertIn("使用 Python 开发", match.evidence[0])

    def test_short_latin_keyword_uses_word_boundaries(self):
        ai_skill = {**PYTHON, "label": "AI", "keywords": ["ai"]}
        match = classify_skill_evidence(ai_skill, "Email: candidate@example.com. I maintain data pipelines.")
        self.assertEqual(match.status, "not_found")
```

Add regression tests to `tests/test_matcher.py` asserting that negation and keyword stuffing cannot produce `keyword_coverage == 100`.

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
python -m unittest tests.test_evidence tests.test_matcher -v
```

Expected: FAIL on missing module and current false-positive behavior.

- [ ] **Step 3: Implement the evidence value object**

Create `api/evidence.py`:

```python
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class EvidenceMatch:
    status: str
    evidence: tuple[str, ...]
    matched_keywords: tuple[str, ...]
    reason: str


NEGATION_PATTERNS = (
    r"不熟悉", r"不了解", r"不会", r"没有.{0,8}经验", r"未使用", r"从未",
    r"\bno\b.{0,16}\bexperience\b", r"\bnever\b", r"\bnot familiar\b",
)
ACTION_PATTERNS = (
    r"负责", r"主导", r"设计", r"开发", r"搭建", r"实现", r"优化", r"部署", r"上线",
    r"\bbuilt\b", r"\bdeveloped\b", r"\bdesigned\b", r"\bimplemented\b", r"\bdeployed\b",
)
```

Implement `_keyword_spans`, `_line_for_span`, `_is_negated`, and `_has_action_context`. Latin keywords of three or fewer characters must use `(?<![A-Za-z0-9])keyword(?![A-Za-z0-9])`; CJK keywords use escaped literal matching. Evidence is the complete trimmed source line, capped at 240 characters.

Classification order is:

1. no keyword span → `not_found / no_keyword`;
2. all spans negated → `not_found / explicit_negation`;
3. at least one non-negated span on an action/project line → `evidenced / action_context`;
4. non-negated spans only in skills/list-like context → `uncertain / keyword_without_experience_context`.

- [ ] **Step 4: Replace `_hit` for resume evidence only**

Keep simple matching for JD knowledge-base discovery temporarily, but use `classify_skill_evidence` for all resume statuses, coverage counts, ledger entries, and rewrite selection. Do not use `_hit_score` to label anything “confirmed”.

- [ ] **Step 5: Run counterexamples and full suite**

```bash
python -m unittest tests.test_evidence tests.test_matcher -v
python -m unittest discover -s tests -v
```

Expected: all PASS; both counterexamples no longer report complete evidenced coverage.

- [ ] **Step 6: Commit**

```bash
git add api/evidence.py api/matcher.py tests/test_evidence.py tests/test_matcher.py
git commit -m "fix: classify resume evidence with context"
```

---

### Task 6: Versioned Analysis Contract and Fact-Safe Rewrite Results

**Day:** 3–4

**Files:**
- Modify: `api/matcher.py`
- Modify: `api/knowledge.py`
- Modify: `api/main.py`
- Create: `tests/test_api_contract.py`
- Modify: `tests/test_api_entrypoint.py`

**Interfaces:**
- Consumes: Task 3 validation/errors, Task 4 parser, Task 5 evidence engine.
- Produces: `analyze_public_beta(jd_text: str, resume_text: str, analysis_id: str, role: str | None = None) -> dict` and the `POST /api/v1/analyses` response schema consumed by Tasks 8 and 10.

- [ ] **Step 1: Write contract tests before changing the endpoint**

Create `tests/test_api_contract.py` using `fastapi.testclient.TestClient`:

```python
import unittest
from fastapi.testclient import TestClient
from api.main import create_app


class AnalysisContractTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(create_app(serve_static=False))

    def test_short_jd_returns_structured_400(self):
        response = self.client.post("/api/v1/analyses", data={"jd": "too short", "privacy_consent_version": "2026-08-11"})
        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertEqual(body["error_code"], "JD_TOO_SHORT")
        self.assertTrue(body["request_id"])

    def test_success_has_versions_requirements_and_coverage(self):
        response = self.client.post(
            "/api/v1/analyses",
            data={"jd": "We require Python and RAG experience in deployed projects. " * 2, "role": "ai_agent", "privacy_consent_version": "2026-08-11"},
            files={"resume": ("resume.txt", "项目经验：使用 Python 开发并部署数据服务。", "text/plain")},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertRegex(body["analysis_id"], r"^[a-f0-9]{32}$")
        self.assertEqual(body["algorithm_version"], "evidence-v1")
        self.assertIn("knowledge_base_version", body)
        self.assertIn("requirements", body)
        self.assertIn("coverage_summary", body)
        self.assertNotIn("five_dim_review", body)
```

- [ ] **Step 2: Run contract tests and verify failure**

Run: `python -m unittest tests.test_api_contract -v`

Expected: FAIL because the route and response contract do not exist.

- [ ] **Step 3: Make `create_app` explicitly configurable**

Change the signature to:

```python
def create_app(serve_static: bool | None = None) -> FastAPI:
```

When `serve_static is None`, keep the current environment-based behavior. Tests pass `False` so route matching cannot be shadowed by static mounting.

- [ ] **Step 4: Build the new response in `matcher.py`**

Add these internal helpers before constructing the response: `split_jd_statements(jd_text: str) -> list[str]`, `classify_requirement_priority(statement: str, known: bool) -> str`, `build_requirements(jd_text: str, skills: list[dict], resume_text: str) -> list[dict]`, and `analyze_public_beta(jd_text: str, resume_text: str, analysis_id: str, role: str | None = None) -> dict`.

`split_jd_statements` splits on newlines and Chinese/English sentence terminators, trims bullet prefixes, drops statements shorter than 6 characters, caps each statement at 300 characters, and preserves first-seen order. For each known skill, `build_requirements` uses the first statement containing one of its boundary-aware keywords as `jd_evidence`. Priority is `preferred` when that statement contains `加分`, `优先`, `preferred`, or `nice to have`; otherwise it is `required`. A statement with requirement language (`必须`, `要求`, `需要`, `职责`, `任职`, `must`, `required`, `responsible`) but no known skill becomes an `unknown` requirement. Its ID is `unknown-` plus the first 12 hexadecimal characters of `sha256(normalized_statement.encode("utf-8"))`. If the JD has no known skill at all, return up to the first 12 non-empty statements as `unknown` rather than substituting the entire role template.

The public response must have this exact top-level shape:

```python
{
    "ok": True,
    "analysis_id": analysis_id,
    "algorithm_version": ALGORITHM_VERSION,
    "knowledge_base_version": KNOWLEDGE_BASE_VERSION,
    "role": {"id": role_key, "label": spec["label"], "confidence": role_confidence},
    "coverage_summary": {
        "known_requirement_count": known,
        "unknown_requirement_count": unknown,
        "evidenced_count": evidenced,
        "uncertain_count": uncertain,
        "missing_evidence_count": missing,
        "keyword_coverage": round(evidenced / known * 100) if known else None,
    },
    "requirements": requirements,
    "rewrite_suggestions": suggestions,
    "warnings": warnings,
}
```

Each requirement contains:

```python
{
    "requirement_id": skill["id"],
    "label": skill["label"],
    "priority": "required" | "preferred" | "unknown",
    "jd_evidence": exact_jd_line,
    "resume_status": "evidenced" | "uncertain" | "not_found",
    "resume_evidence": list(evidence_match.evidence),
    "reason": evidence_match.reason,
}
```

If no known skill is found in the JD, do not fall back to the full role template. Return `keyword_coverage: null`, populate `warnings` with `KNOWN_REQUIREMENT_COVERAGE_LOW`, and display unknown JD lines.

- [ ] **Step 5: Make rewrite suggestions user-decision ready**

Each suggestion contains:

```python
{
    "suggestion_id": "rw-001",
    "source": original_line,
    "suggested": draft,
    "requirement_ids": [skill_id],
    "fact_status": "confirmed_source_only" | "pending_confirmation",
    "pending_fields": ["metric", "time_range", "personal_contribution"],
    "default_export": fact_status == "confirmed_source_only",
}
```

The server never writes a fabricated number into `suggested`. A prompt to add a number belongs in `pending_fields`, not inside the resume sentence.

- [ ] **Step 6: Add the versioned endpoint and legacy redirect window**

Add `POST /api/v1/analyses` as the public contract. Its HTTP handler creates `analysis_id = secrets.token_hex(16)`, validates/parses inputs, and passes that ID to `analyze_public_beta`; it does not reconstruct response fields. Keep `/api/analyze` for one release as a thin compatibility route that calls the same handler and adds response header `Deprecation: true`; the frontend switches in Task 8.

Validate `privacy_consent_version` equals the configured version. A mismatch returns 400 `PRIVACY_CONSENT_REQUIRED`.

- [ ] **Step 7: Run contract, matcher, and full tests**

```bash
python -m unittest tests.test_api_contract tests.test_matcher tests.test_api_entrypoint -v
python -m unittest discover -s tests -v
```

Expected: all PASS.

- [ ] **Step 8: Commit**

```bash
git add api/main.py api/matcher.py api/knowledge.py tests/test_api_contract.py tests/test_api_entrypoint.py
git commit -m "feat: add versioned evidence analysis contract"
```

---

### Task 7: Mobile-Safe and Accessible Application Shell

**Day:** 4

**Files:**
- Modify: `index.html`
- Modify: `app.js`
- Modify: `styles.css`
- Modify: `e2e/public-beta.spec.js`

**Interfaces:**
- Consumes: Task 2 public scope and Task 6 public response naming.
- Produces: a responsive shell with `#app > .app-shell`, accessible inputs, and stable `data-testid` locators for Task 8.

- [ ] **Step 1: Add failing mobile and accessibility checks**

Append:

```javascript
test("390px shell has no page overflow and sidebar starts closed", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  const metrics = await page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
    sidebarTransform: getComputedStyle(document.querySelector(".sidebar")).transform
  }));
  expect(metrics.scrollWidth).toBeLessThanOrEqual(metrics.clientWidth);
  expect(metrics.sidebarTransform).not.toBe("none");
});

test("core form is keyboard-addressable", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByLabel("岗位 JD")).toBeVisible();
  await expect(page.getByLabel("上传简历")).toBeAttached();
  await expect(page.getByLabel(/我已阅读并同意/)).toBeAttached();
});
```

- [ ] **Step 2: Verify the mobile test fails on the root-binding bug**

Run: `npm run test:e2e -- --project mobile-390 --grep "390px shell"`

Expected: FAIL with page scroll width larger than viewport or sidebar transform `none`.

- [ ] **Step 3: Fix the Vue mount boundary**

Change the root structure from binding classes on the mount element to:

```html
<div id="app">
  <div :class="['app-shell', appShellClass]">
  </div>
</div>
```

Move every current sidebar and main-shell child between the inner opening and closing tags; the snippet shows the boundary only and must not leave the app shell empty. The dynamic class must be on the inner element because Vue compiles the mount element’s contents, not directives on the mount element itself.

- [ ] **Step 4: Make controls semantic**

- Use real `<button disabled>` for unavailable actions, not a `.disabled` class only.
- Keep file input visually hidden with a screen-reader-safe utility class, not `display:none`.
- Associate `label for="jd-input"` and `textarea id="jd-input"`.
- Associate `label for="resume-input"` and `input id="resume-input"`.
- Add `aria-live="polite"` to loading status and `role="alert"` to errors.
- Add visible `:focus-visible` outlines to links, buttons, inputs, and textareas.

- [ ] **Step 5: Add responsive CSS assertions**

At widths ≤960px:

- `.main-shell { margin-left: 0; }`
- `.sidebar { transform: translateX(-100%); max-width: min(320px, 86vw); }`
- `.sidebar-open .sidebar { transform: translateX(0); }`
- `.container`, `.card`, `.topbar` have `min-width:0` and no fixed width.
- tables remain inside their own `overflow-x:auto` container.

At widths ≤640px, stack result cards and actions vertically without shrinking buttons below 44px height.

- [ ] **Step 6: Run desktop and mobile E2E**

```bash
npm run check
npm run test:e2e -- --grep "390px shell|keyboard-addressable"
```

Expected: PASS on both configured projects.

- [ ] **Step 7: Commit**

```bash
git add index.html app.js styles.css e2e/public-beta.spec.js
git commit -m "fix: make public beta shell mobile accessible"
```

---

### Task 8: Core Review, User Decisions, and Safe Export

**Day:** 4–5

**Files:**
- Modify: `index.html`
- Modify: `app.js`
- Modify: `styles.css`
- Modify: `e2e/public-beta.spec.js`
- Create: `tests/fixtures/resume.txt`
- Create: `tests/fixtures/jd.txt`

**Interfaces:**
- Consumes: Task 6 `/api/v1/analyses` schema and Task 7 shell.
- Produces: requirement review cards, `suggestionDecisions`, and an export containing only accepted/edited suggestions.

- [ ] **Step 1: Add deterministic synthetic fixtures**

`tests/fixtures/jd.txt`:

```text
我们招聘 AI 产品实习生。必须能够进行用户研究、需求分析和 PRD 撰写，并推动一个 AI 应用从 0 到 1 上线。熟悉 RAG 或 Prompt Engineering 为加分项。候选人需要能够用真实数据复盘产品效果。
```

`tests/fixtures/resume.txt`:

```text
联系方式：audit@example.com

教育背景
某大学 计算机科学 本科

项目经验
主导 AI 求职助手从 0 到 1 上线，完成用户访谈、需求分析和 PRD 撰写。
使用 Python 与 FastAPI 开发规则分析服务，邀请 20 名同学试用。

技能
Python、FastAPI、Vue
```

- [ ] **Step 2: Write the complete happy-path E2E before implementation**

```javascript
test("user reviews evidence, accepts one suggestion, and exports only accepted work", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("岗位 JD").fill(require("fs").readFileSync("tests/fixtures/jd.txt", "utf8"));
  await page.getByLabel("上传简历").setInputFiles("tests/fixtures/resume.txt");
  await page.getByLabel(/我已阅读并同意/).check();
  await page.getByRole("button", { name: "分析这份简历" }).click();
  await expect(page.getByRole("heading", { name: "JD 要求与简历证据" })).toBeVisible();
  await expect(page.getByText("关键词覆盖")).toBeVisible();
  await expect(page.getByText("简历可信度")).toHaveCount(0);
  const firstSuggestion = page.getByTestId("suggestion-card").first();
  await firstSuggestion.getByRole("button", { name: "接受" }).click();
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "导出已确认草稿" }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toContain("简历优化草稿");
});
```

- [ ] **Step 3: Run and verify failure**

Run: `npm run test:e2e -- --grep "reviews evidence"`

Expected: FAIL because the new contract UI and decision controls are absent.

- [ ] **Step 4: Replace legacy score/result sections**

Render these sections in order:

1. role label + confidence warning;
2. coverage summary (`keyword_coverage`, known, unknown, evidenced, uncertain, not found);
3. requirements grouped by priority;
4. each requirement’s JD evidence, resume status, and resume evidence;
5. rewrite cards;
6. export and feedback.

Do not render `five_dim_review`, overall score ring, learning path, or interview data even if a legacy response contains them.

- [ ] **Step 5: Add frontend state and timeout**

Use this state shape:

```javascript
const suggestionDecisions = reactive({});
// suggestionDecisions[id] = { decision: "accepted" | "edited" | "rejected", text: string }
```

In `submit`, create an `AbortController`, set a 22-second timer, call `/api/v1/analyses`, and clear the timer in `finally`. Map `error_code` to a visible user message and show the response `request_id` for support.

- [ ] **Step 6: Implement decision-safe export**

`downloadConfirmedDraft` filters to `accepted` and `edited`. It excludes `pending_confirmation` unless the user edited the suggestion and explicitly checked `已确认补充事实真实`. The Markdown begins with:

```markdown
# JD 定制简历草稿

> 本草稿由用户确认的原文与修改组成；请在投递前进行最终人工检查。
```

- [ ] **Step 7: Run tests**

```bash
npm run check
npm run test:e2e -- --grep "reviews evidence"
python -m unittest discover -s tests -v
```

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add index.html app.js styles.css e2e/public-beta.spec.js tests/fixtures/jd.txt tests/fixtures/resume.txt
git commit -m "feat: add evidence review and safe export flow"
```

---

### Task 9: Privacy-Safe Telemetry, Request IDs, and Security Headers

**Day:** 5

**Files:**
- Create: `api/telemetry.py`
- Create: `tests/test_telemetry.py`
- Modify: `api/errors.py`
- Modify: `api/main.py`
- Modify: `app.js`
- Modify: `vercel.json`
- Create: `docs/metrics/public-beta-events.md`

**Interfaces:**
- Produces: `safe_event(event_name: str, attributes: dict) -> dict`, `POST /api/v1/events` returning 204, `X-Request-ID`, and security headers.
- Consumed by: Task 12 release checks.

- [ ] **Step 1: Write allowlist and PII rejection tests**

Create the documentation directory first:

```bash
mkdir -p docs/metrics
```

Create `tests/test_telemetry.py`:

```python
import unittest
from fastapi.testclient import TestClient
from api.main import create_app
from api.telemetry import safe_event


class TelemetryTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(create_app(serve_static=False))

    def test_only_allowlisted_fields_survive(self):
        event = safe_event("analysis_succeeded", {
            "analysis_id": "a" * 32,
            "file_type": "txt",
            "processing_ms": 120,
            "algorithm_version": "evidence-v1",
            "resume_text": "private",
            "filename": "Jane-Doe-resume.txt",
        })
        self.assertEqual(event["attributes"], {
            "analysis_id": "a" * 32,
            "file_type": "txt",
            "processing_ms": 120,
            "algorithm_version": "evidence-v1",
        })

    def test_unknown_event_is_rejected(self):
        with self.assertRaises(ValueError):
            safe_event("raw_resume_uploaded", {"file_type": "txt"})

    def test_pii_hidden_inside_allowed_field_is_rejected(self):
        with self.assertRaises(ValueError):
            safe_event("suggestion_rejected", {"analysis_id": "a" * 32, "suggestion_id": "rw-001", "reason_code": "email-me@example.com"})

    def test_event_body_over_four_kib_is_rejected(self):
        response = self.client.post("/api/v1/events", content=b"x" * 4097, headers={"content-type": "application/json"})
        self.assertEqual(response.status_code, 413)
```

- [ ] **Step 2: Run and verify failure**

Run: `python -m unittest tests.test_telemetry -v`

Expected: ERROR importing missing module.

- [ ] **Step 3: Implement a strict event schema**

Allow only these event names:

```python
EVENT_FIELDS = {
    "page_viewed": {"device_category", "referrer_category"},
    "analysis_started": {"analysis_id", "file_type", "file_size_bucket", "jd_length_bucket", "algorithm_version"},
    "upload_validation_failed": {"analysis_id", "error_code", "file_type", "file_size_bucket"},
    "analysis_succeeded": {"analysis_id", "file_type", "processing_ms", "algorithm_version", "known_count", "unknown_count", "evidenced_count", "uncertain_count"},
    "analysis_failed": {"analysis_id", "error_code", "processing_ms", "retryable"},
    "evidence_viewed": {"analysis_id", "requirement_id", "resume_status"},
    "suggestion_accepted": {"analysis_id", "suggestion_id", "algorithm_version"},
    "suggestion_edited": {"analysis_id", "suggestion_id", "confirmed_pending_facts"},
    "suggestion_rejected": {"analysis_id", "suggestion_id", "reason_code"},
    "draft_exported": {"analysis_id", "format", "suggestion_count", "pending_count"},
    "feedback_submitted": {"analysis_id", "rating", "reason_code"},
}
```

Reuse the random 32-character hexadecimal `analysis_id` introduced in Task 6 for started/success/failure events and the response. Frontend evidence, decision, export, and feedback events reuse only that returned ID. It is an opaque correlation ID, never derived from user input.

`safe_event` returns a new dict containing only allowlisted keys. Require `analysis_id` on every event except `page_viewed`, validate it against `^[a-f0-9]{32}$`, validate other categorical values against documented enums, identifiers against `^[a-z0-9_-]{1,64}$`, booleans as booleans, and numeric values as non-negative finite numbers. Reject the whole event if any value matches an email, phone-like sequence, URL, newline, or exceeds 64 characters. Serialize accepted events as one JSON log line. Never pass request bodies or exceptions containing raw inputs to the logger.

- [ ] **Step 4: Add request ID middleware and error handlers**

For every request, accept a syntactically valid `X-Request-ID` of at most 64 safe characters or generate `uuid.uuid4().hex`. Return it in response headers and error JSON. Register handlers for `ApiError`, FastAPI validation errors, and generic exceptions. Generic errors log only exception class, request ID, route name, and duration.

- [ ] **Step 5: Add telemetry endpoint and frontend helper**

`POST /api/v1/events` reads at most 4 KiB before JSON parsing, accepts only event name and attributes, sanitizes them with `safe_event`, logs the sanitized result, and returns status 204. Oversized bodies return 413 `EVENT_TOO_LARGE`.

In `app.js`:

```javascript
const trackEvent = (name, attributes = {}) => {
  const body = JSON.stringify({ name, attributes });
  if (navigator.sendBeacon) {
    navigator.sendBeacon("/api/v1/events", new Blob([body], { type: "application/json" }));
    return;
  }
  fetch("/api/v1/events", { method: "POST", headers: { "content-type": "application/json" }, body, keepalive: true }).catch(() => {});
};
```

Call it only with enumerated/aggregated values from the event dictionary.

- [ ] **Step 6: Add same-origin CORS and security headers**

Replace `allow_origins=["*"]` with `ALLOWED_ORIGINS`. Add these Vercel headers for `/(.*)`:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
        { "key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=()" },
        { "key": "Content-Security-Policy", "value": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'" }
      ]
    }
  ]
}
```

- [ ] **Step 7: Document exact event equations**

`docs/metrics/public-beta-events.md` repeats the event names, allowed attributes, and these equations:

- analysis success rate = `analysis_succeeded / analysis_started`;
- effective suggestion adoption = distinct `analysis_id` with accepted, edited, or exported suggestion / distinct successful `analysis_id`;
- export rate = distinct exported `analysis_id` / distinct successful `analysis_id`;
- helpful rate = positive `feedback_submitted / all feedback_submitted`.

- [ ] **Step 8: Configure operational views and alerts**

In Vercel Observability, save production views for `analysis_started`, `analysis_succeeded`, `analysis_failed`, HTTP 5xx, `processing_ms`, and `error_code`. Configure these launch alerts:

- health endpoint fails twice consecutively → page the release owner;
- 5xx rate ≥1% over 5 minutes or 3 5xx responses in 5 minutes → rollback review;
- p95 analysis latency exceeds 12 seconds for 10 minutes → capacity investigation;
- any telemetry/PII rejection counter above zero → disable telemetry and start privacy review;
- analysis success rate below 98% over the gray window → No-Go.

Trigger one synthetic failure and record the received alert under `Launch verification` in `docs/metrics/public-beta-events.md`; Task 12 copies the evidence into the release runbook. If the current Vercel plan cannot express these views or alerts, G3 remains blocked until the product owner selects and configures an external uptime/error-monitoring provider; “we will watch logs manually” is insufficient for public Beta.

- [ ] **Step 9: Run tests**

```bash
python -m unittest tests.test_telemetry tests.test_api_contract -v
python -m unittest discover -s tests -v
npm run check
```

Expected: PASS.

- [ ] **Step 10: Commit**

```bash
git add api/telemetry.py api/errors.py api/main.py app.js vercel.json tests/test_telemetry.py docs/metrics/public-beta-events.md
git commit -m "feat: add privacy-safe beta telemetry"
```

---

### Task 10: Frozen Quality Evaluation Set and Deterministic Evaluator

**Day:** 5–6

**Files:**
- Create: `evals/public_beta_cases.jsonl`
- Create: `scripts/evaluate_public_beta.py`
- Create: `tests/test_evaluator.py`
- Create: `docs/quality/public-beta-evaluation.md`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: `analyze_public_beta` from Task 6.
- Produces: `python scripts/evaluate_public_beta.py --cases evals/public_beta_cases.jsonl --report artifacts/public-beta-quality-report.json --require-gold`, with machine-readable gold and full-set metrics consumed by Task 13.

- [ ] **Step 1: Write failing evaluator schema and metric tests**

Create the evaluation directories first:

```bash
mkdir -p evals scripts docs/quality
```

Create `tests/test_evaluator.py` around three in-memory cases and require:

- duplicate `case_id` fails validation;
- a file not containing exactly 150 cases fails in release mode;
- `--require-gold` fails unless exactly 30 cases have `gold_approved=true`, non-null `reviewed_by`, and an ISO-8601 `reviewed_at`;
- evidence precision counts a positive claim only when the returned status is `evidenced`;
- negation pass rate counts a case only when every explicitly negated requirement is not `evidenced`;
- fabricated fact rate flags a concrete number, tool, ownership claim, or outcome absent from both source and approved facts;
- the report contains numerator, denominator, rate, case IDs for every failure, `algorithm_version`, and `knowledge_base_version`.

- [ ] **Step 2: Run tests and verify failure**

Run: `python -m unittest tests.test_evaluator -v`

Expected: FAIL because the evaluator does not exist.

- [ ] **Step 3: Implement the case schema and evaluator**

Each JSONL line has this exact shape:

```json
{
  "case_id": "gold-candidate-001",
  "category": "negation_zh",
  "jd": "我们要求候选人具备 Python 项目经验。",
  "resume": "我没有 Python 项目经验，曾负责用户访谈。",
  "expected_requirements": [
    {"requirement_id": "aa_py", "allowed_statuses": ["not_found"]}
  ],
  "approved_facts": [],
  "forbidden_suggestion_tokens": ["Python 项目经验"],
  "gold_candidate": true,
  "gold_approved": false,
  "reviewed_by": null,
  "reviewed_at": null,
  "independent_review_status": "pending"
}
```

The evaluator imports production functions; it must not duplicate matching logic. For a deterministic response ID, it passes the first 32 hexadecimal characters of `sha256(case_id.encode("utf-8"))` to `analyze_public_beta`. It validates every line before evaluation, writes JSON only to the path passed with `--report`, creates the report directory if absent, and exits non-zero when schema, cardinality, gold approval, or metric gates fail. Add `artifacts/` to `.gitignore` because reports can be regenerated.

Use these equations:

- evidence precision = correct `evidenced` claims / all returned `evidenced` claims on approved gold cases;
- negation pass rate = negation cases with no contradicted positive status / all negation cases;
- fabricated fact rate = suggestions containing unsupported concrete facts / all generated suggestions. A suggestion is unsupported when it contains any case-specific `forbidden_suggestion_tokens`, or a numeric token absent from `resume` plus `approved_facts`; tool, ownership, and outcome traps must be listed explicitly in `forbidden_suggestion_tokens` so this check is deterministic;
- status agreement = requirements whose returned status is in `allowed_statuses` / all labeled requirements.

- [ ] **Step 4: Build the fixed 150-case distribution**

Create exactly 150 non-sensitive cases with stable IDs and this distribution:

- 30 explicit-negation cases: 15 Chinese and 15 English;
- 25 keyword-list and token-boundary cases;
- 35 clear positive project/action evidence cases;
- 20 JDs with unknown or unsupported knowledge-base requirements;
- 20 rewrite factuality cases containing tempting but unsupported metrics/tools/ownership;
- 20 mixed or ambiguous cases that should return `uncertain`.

Designate five cases from each category as the 30 gold candidates. An evaluation Agent may generate candidates, but a different QA Agent must inspect all 120 non-gold cases and change `independent_review_status` from `pending` to `approved` or `rejected`. Only the human product owner may set `gold_approved=true` and populate `reviewed_by`/`reviewed_at`; Agent self-labels never satisfy the gold gate.

- [ ] **Step 5: Document review ownership and gates**

`docs/quality/public-beta-evaluation.md` records:

- case distribution and schema version `public-beta-eval-v1`;
- generator identity and independent reviewer identity;
- all rejected or corrected case IDs and reasons;
- the 30 gold-candidate IDs;
- product-owner review status;
- required gates: evidence precision ≥95%, negation pass 100%, fabricated fact rate 0%;
- command and report SHA-256 used for G3.

- [ ] **Step 6: Run the evaluator in pre-approval and release modes**

```bash
python -m unittest tests.test_evaluator -v
python scripts/evaluate_public_beta.py --cases evals/public_beta_cases.jsonl --report artifacts/public-beta-quality-report.json
python scripts/evaluate_public_beta.py --cases evals/public_beta_cases.jsonl --report artifacts/public-beta-quality-report.json --require-gold
```

Expected before human review: unit tests pass; the first evaluator command reports full-set regressions; `--require-gold` exits non-zero and explicitly lists unapproved gold candidate IDs. Expected after review: all 150 cases validate, all 120 non-gold cases have independent approval, exactly 30 gold cases have product-owner approval, and all three release metric gates pass.

- [ ] **Step 7: Commit code, cases, and review record**

```bash
git add evals/public_beta_cases.jsonl scripts/evaluate_public_beta.py tests/test_evaluator.py docs/quality/public-beta-evaluation.md .gitignore
git commit -m "test: add frozen public beta quality evaluation"
```

---

### Task 11: Abuse Controls, Adversarial Regression, and Performance Budget

**Day:** 5–6

**Files:**
- Modify: `api/main.py`
- Modify: `api/config.py`
- Modify: `tests/test_api_contract.py`
- Create: `tests/test_adversarial.py`
- Modify: `e2e/public-beta.spec.js`

**Interfaces:**
- Consumes: versioned endpoint and telemetry.
- Produces: `run_analysis(jd_text: str, upload: ValidatedUpload, analysis_id: str) -> dict`, per-instance concurrency backstop, explicit 429/504 behavior, and a platform rate-limit verification requirement.

- [ ] **Step 1: Write failure tests for timeout and concurrent saturation**

Use patches so tests do not sleep:

```python
def test_analysis_timeout_returns_504(self):
    with patch("api.main.run_analysis", side_effect=TimeoutError):
        response = self._valid_request()
    self.assertEqual(response.status_code, 504)
    self.assertEqual(response.json()["error_code"], "ANALYSIS_TIMEOUT")

def test_concurrency_saturation_returns_429(self):
    with patch("api.main.ANALYSIS_SEMAPHORE.acquire", return_value=False):
        response = self._valid_request()
    self.assertEqual(response.status_code, 429)
    self.assertTrue(response.json()["retryable"])
```

- [ ] **Step 2: Add adversarial regression tests**

`tests/test_adversarial.py` must cover:

- negation in Chinese and English;
- keyword list with no action context;
- `ai` inside `email`, `maintain`, and URL text;
- a JD containing no known skill;
- corrupted PDF/DOCX;
- ZIP compression ratio over 100;
- 11-page PDF;
- 5 MiB + 1 byte file;
- fake extension;
- generated suggestion with a number absent from the source;
- log event containing email/phone/resume fields.

- [ ] **Step 3: Implement a local concurrency backstop**

Add this constant to `api/config.py`; reuse `ANALYSIS_TIMEOUT_SECONDS` from Task 3:

```python
MAX_CONCURRENT_ANALYSES = 2
```

In `api/main.py`, put the existing parse/match/response construction behind this exact boundary:

```python
ANALYSIS_SEMAPHORE = threading.BoundedSemaphore(MAX_CONCURRENT_ANALYSES)


def run_analysis(jd_text: str, upload: ValidatedUpload, analysis_id: str) -> dict:
    """Execute validated parsing and evidence analysis without HTTP concerns."""
    resume_text = parse_validated_resume(upload)
    return analyze_public_beta(jd_text, resume_text, analysis_id)


def _run_analysis_and_release(jd_text: str, upload: ValidatedUpload, analysis_id: str) -> dict:
    try:
        return run_analysis(jd_text, upload, analysis_id)
    finally:
        ANALYSIS_SEMAPHORE.release()


async def run_analysis_with_limits(jd_text: str, upload: ValidatedUpload, analysis_id: str) -> dict:
    if not ANALYSIS_SEMAPHORE.acquire(blocking=False):
        raise ApiError(429, "ANALYSIS_BUSY", "当前分析请求较多，请稍后重试。", retryable=True)
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(_run_analysis_and_release, jd_text, upload, analysis_id),
            timeout=ANALYSIS_TIMEOUT_SECONDS,
        )
    except TimeoutError as exc:
        raise ApiError(504, "ANALYSIS_TIMEOUT", "分析超时，请缩短内容后重试。", retryable=True) from exc
```

Import `asyncio` and `threading`. Use a non-blocking semaphore with maximum 2 active analyses per serverless instance. Failure returns 429 `ANALYSIS_BUSY`. This is a resource backstop, not the public IP rate limit.

The semaphore release must remain inside the worker wrapper, not an endpoint `finally` block: after a 504 the worker thread may still be finishing, so the slot stays occupied until real work ends. Return 504 `ANALYSIS_TIMEOUT` without logging input bodies.

- [ ] **Step 4: Configure and verify platform rate limiting**

The deploy Agent configures Vercel project firewall rules for `POST /api/v1/analyses` at 10 requests per source IP per rolling hour and `POST /api/v1/events` at 120 requests per source IP per rolling hour, action `deny`, response 429. If the current Vercel plan cannot create the analysis rule, G3 is blocked until the product owner chooses one of these explicit mitigations:

1. upgrade/configure a platform plan with shared rate limiting; or
2. put the endpoint behind a shared rate-limiting edge/provider.

Do not claim an in-memory counter provides global serverless rate limiting.

- [ ] **Step 5: Add a simple performance regression command**

Add a test that performs 20 synthetic TXT analyses against local TestClient, records durations, and asserts no single request exceeds 2 seconds on the test machine. Treat this as regression detection, not the production p95 claim.

- [ ] **Step 6: Run all quality gates**

```bash
python -m unittest tests.test_adversarial tests.test_api_contract -v
python -m unittest discover -s tests -v
npm run test:e2e
```

Expected: all PASS. Separately capture evidence that the 11th production-like request receives 429 from the platform rule before G3.

- [ ] **Step 7: Commit**

```bash
git add api/main.py api/config.py tests/test_api_contract.py tests/test_adversarial.py e2e/public-beta.spec.js
git commit -m "test: enforce beta abuse and adversarial gates"
```

---

### Task 12: Production Smoke Test, Release Runbook, and Rollback Drill

**Day:** 6

**Files:**
- Create: `scripts/smoke_public_beta.py`
- Create: `docs/runbooks/public-beta-release.md`
- Modify: `README.md`
- Modify: `PROJECT_RECORD.md`

**Interfaces:**
- Consumes: health, `/api/v1/analyses`, fixture inputs, versions, and platform rate limit.
- Produces: one command that proves production health and synthetic analysis; exact release and rollback steps for Task 13.

- [ ] **Step 1: Write the smoke script with explicit assertions**

Create the release directories first:

```bash
mkdir -p scripts docs/runbooks
```

`scripts/smoke_public_beta.py` accepts exactly one positional base URL. It must:

1. GET `/api/health`, assert 200 and `{"status":"ok"}`;
2. POST `/api/v1/analyses` with `tests/fixtures/jd.txt` and `tests/fixtures/resume.txt` using multipart;
3. assert 200, `ok=true`, both version fields, at least one requirement, and no `five_dim_review`;
4. assert no response object contains raw-input keys named `resume_text` or `job_description`, and response text does not contain the fixture-only PII marker `audit@example.com`; evidence excerpts from actual work-history lines remain allowed;
5. print only status, versions, counts, and elapsed milliseconds.

Use Python standard library `urllib.request`; do not add a production dependency for this script.

- [ ] **Step 2: Test smoke against local server**

Run server:

```bash
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

In another shell:

```bash
python scripts/smoke_public_beta.py http://127.0.0.1:8000
```

Expected output shape:

```text
health=ok
analysis=ok algorithm=evidence-v1 requirements=5 elapsed_ms=240
```

- [ ] **Step 3: Write the release runbook**

`docs/runbooks/public-beta-release.md` includes exact sections:

- prerequisites and required approvals;
- commands for Python tests, JS check, E2E, and smoke;
- review of current `git status` and commit SHA;
- Vercel preview deployment validation;
- production deployment and smoke;
- verification of CSP/CORS/security headers;
- verification that 11th request receives 429;
- two-hour 5–10-user gray period;
- monitoring thresholds from the design doc;
- rollback to the previous Vercel deployment within 10 minutes;
- conditions to disable upload entirely;
- incident record fields;
- product-owner Go/No-Go signature.

- [ ] **Step 4: Update project docs truthfully**

README and PROJECT_RECORD must describe the public Beta contract, supported formats, no-persistence application policy, limits, local setup, full verification commands, and known limitations. Remove stale statements claiming full bilingual results, `.doc` support, offline Web use, or broad four-mode public scope.

- [ ] **Step 5: Run documentation and smoke checks**

```bash
python scripts/smoke_public_beta.py http://127.0.0.1:8000
rg -n "\.doc\b|离线可用|无第三方上传|完整英文|五维评审" README.md PROJECT_RECORD.md
git diff --check
```

Expected: smoke passes; no current public claim contradicts the Beta; `git diff --check` has no output.

- [ ] **Step 6: Commit**

```bash
git add scripts/smoke_public_beta.py docs/runbooks/public-beta-release.md README.md PROJECT_RECORD.md
git commit -m "docs: add public beta release runbook"
```

---

### Task 13: Release Candidate Review and Public Go/No-Go

**Day:** 6–7

**Files:**
- Modify only if a verified release-blocking defect is found.
- Record: `docs/runbooks/public-beta-release.md`

**Interfaces:**
- Consumes: all prior task commits.
- Produces: signed G3 QA/security/quality decision and human product-owner G4 Go/No-Go decision.

- [ ] **Step 1: Freeze release candidate**

Record commit SHA and prohibit feature changes. Only P0/P1 release-blocking fixes are accepted after this point.

- [ ] **Step 2: Run the complete local gate from a clean environment**

```bash
python -m pip install -r dev-requirements.txt
python -m unittest discover -s tests -v
python scripts/evaluate_public_beta.py --cases evals/public_beta_cases.jsonl --report artifacts/public-beta-quality-report.json --require-gold
shasum -a 256 artifacts/public-beta-quality-report.json
npm ci
npm run check
npx playwright install chromium
npm run test:e2e
git diff --check
git status --short
```

Expected: every test and all three release quality gates pass; record the report SHA-256 in the runbook; `git diff --check` is empty; status contains no unexplained release-code changes.

- [ ] **Step 3: Require independent reviews**

- QA reviewer checks every FR/NFR and E2E result.
- QA reviewer also completes the compatibility matrix on current stable Chrome, Safari, and Edge, plus one iOS Safari and one Android Chrome spot check; device, OS, browser version, and outcome go in the runbook.
- Security/privacy reviewer inspects upload limits, logs, event allowlist, CORS, CSP, rate limit, and legal pages.
- Quality reviewer runs the 150-case set and reports the 30 product-owner-reviewed gold cases separately.
- Each reviewer writes pass/fail with evidence. The implementer cannot serve as reviewer.

- [ ] **Step 4: Deploy preview and run production-shaped validation**

Run:

```bash
python scripts/smoke_public_beta.py "$EJT_PREVIEW_URL"
```

Immediately before running the command, the deploy agent sets `EJT_PREVIEW_URL` to the exact HTTPS preview URL emitted by Vercel, records that exact URL in the runbook, and captures status/headers without storing resume text. An empty variable is a hard failure; the smoke script must reject non-HTTPS remote URLs.

- [ ] **Step 5: Deploy production without promotion traffic**

Run production smoke:

```bash
python scripts/smoke_public_beta.py https://easy-job-tutor-web.vercel.app
```

Verify health, contract, versions, CSP, CORS, telemetry, alerts, and platform 429 behavior. Run ten non-sensitive synthetic analyses for each of TXT, DOCX, and PDF; record p95 by file type and require TXT/DOCX ≤8 seconds and PDF ≤12 seconds.

- [ ] **Step 6: Run 5–10-user gray validation for two hours**

Monitor every 30 minutes:

- health;
- analysis success rate;
- 5xx rate;
- p95 latency;
- parser errors by type;
- PII detector alerts;
- suggestion feedback;
- mobile completion.

Any P0 triggers rollback or upload shutdown immediately.

- [ ] **Step 7: Product owner makes the only Go/No-Go decision**

Go requires all of the following:

- all P0 closed;
- evidence precision ≥95% on 30 gold cases;
- negation set 100% pass;
- fabricated fact rate 0%;
- analysis success ≥98% during gray traffic;
- 5xx <1%;
- mobile core flow passes at 390×844;
- privacy/security review passes;
- rate limit and rollback are proven;
- monitoring and alert tests are visible.

If any item fails, record No-Go, name the blocking task, and keep traffic limited or roll back. The calendar deadline does not override the gate.

- [ ] **Step 8: Record release, do not bundle unrelated changes**

If Go, create one release record commit containing only the completed runbook decision and release metadata:

```bash
git add docs/runbooks/public-beta-release.md
git commit -m "chore: record public beta go-live"
```

---

## Daily Coordination Cadence

### Start of day

- Product owner confirms the day’s gate and scope.
- Coordinator lists active tasks, file ownership, dependencies, and reviewers.
- Every Agent receives only one task card and its prerequisite interfaces.

### Midday integration

- Run affected tests before merging work between tasks.
- Reconcile API/schema changes before frontend/backend continue.
- Update blockers; do not silently change acceptance criteria.

### End of day

- Run the day’s full gate commands.
- Reviewer signs pass/fail with evidence.
- Product owner confirms whether the next wave can start.
- Record scope changes and what was removed in exchange.

## Post-Launch Data Iteration Loop

The monitoring Agent prepares privacy-safe aggregate readouts at +1 day, +3 days, and +7 days. Each readout includes the numerator, denominator, sample size, device split, algorithm version, and knowledge-base version for:

- analysis success and parser failure rate by file type;
- p50/p95 latency by file type;
- effective suggestion adoption, export, and helpful-feedback rates;
- mobile versus desktop core-flow completion difference;
- error codes, PII rejection counters, rate-limit responses, and rollback events.

Do not draw a trend conclusion from fewer than 30 completed analyses. When the sample is sufficient, the Data Agent compares effective suggestion adoption with the 30% target and mobile completion with the ≤15-percentage-point gap guardrail. The Product Agent joins only aggregate event data with coded feedback reasons; raw JD, resume, evidence, suggestion text, and contact details remain unavailable.

For each readout, the Product Agent may propose one core-loop experiment with hypothesis, target metric, guardrail, effort, and rollback condition. No Agent may automatically broaden scope or deploy an experiment: the product owner accepts, rejects, or defers it. PII exposure, fabricated facts, broken upload, or material regression triggers incident handling or rollback rather than experimentation.

## Completion Evidence Required

The implementation is not complete based on deployed appearance or agent reports. Completion requires:

- clean full Python test output;
- clean JS syntax check;
- passing desktop and 390px Playwright suites;
- passing 150-case quality report with separate 30-case gold metrics;
- production smoke output;
- security header and CORS output;
- real platform 429 evidence;
- privacy-safe log/event sample;
- rollback drill record;
- product-owner signed Go decision.
