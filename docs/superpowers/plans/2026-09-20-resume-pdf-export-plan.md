# Task Plan: Frontend Resume PDF Export

## Goal
Let a user turn the analyzed resume into a truthful, ATS-readable (selectable-text) PDF
generated fully in the browser, one click to download, styled per the Skill repo's PDF
design spec.

## Phases
- [x] Phase 1: Build tooling — `package.json`, esbuild bundle of `@hmfw/html-to-pdf`, subset CJK fonts into `fonts/`
- [x] Phase 2: Structured resume form + state (schema, styles, page size, prefill from analysis)
- [x] Phase 3: A4 preview DOM + three styles (modern-minimal / classic-professional / creative-clean)
- [x] Phase 4: One-click export via `htmlToPdf`, lazy-loaded bundle
- [x] Phase 5: Verification — unit tests, headless browser export, PDF text extraction + no-clip check
- [ ] Phase 6: Docs + checkpoint commit

## Key Questions
1. Does `@hmfw/html-to-pdf` render Chinese as selectable vector text with subset fonts in a real browser? (must prove before building UI)
2. Which Skill design tokens survive the library's CSS subset (no gradients / complex flex-grid)?
3. How is the resume content sourced when the browser never receives the parsed resume text?

## Decisions Made
- **Engine**: `@hmfw/html-to-pdf` v2.0.1 (pdf-lib, DOM-layout, vector text, built-in CJK subsetting, no html2canvas). Chosen over jsPDF/pdfmake (no CJK font) and html2canvas (bitmap, violates ATS rule).
- **Fonts**: Source Han Sans SC Regular/Bold, subset with `fonttools` to GB2312 + Latin + punctuation, served same-origin from `/fonts/`; lazy-loaded when the preview opens.
- **Build**: add a minimal esbuild step that emits `vendor/html-to-pdf.browser.js` (IIFE global) plus a copy of the vendored fonts; the app keeps the no-framework-build Vue CDN setup.
- **Content source**: user-entered structured form (name/contact/summary/education/experience/projects/skills/awards), prefilled where the analysis response already has data (target role, bullet-rewrite source lines, matched skills). No resume text is sent to the backend for PDF.
- **Styles**: colors/typography lifted from `Easy-Job-Tutor/scripts/build_resume_pdf.py` and `design/resume-layout-spec.md`.
- **Page**: A4 default, Letter optional, one page preferred; overflow continues to a second page rather than clipping.

## Constraints (from the Skill repo)
- Text-based PDF, selectable/searchable, never an image export.
- No fabricated facts: pending items from `resume_optimization` must stay out of the PDF unless the user explicitly types real content.
- No photos by default, no icons, no skill bars, no complex tables, no heavy color.
- Preview and export must use the same DOM so they match.

## Evidence
- `build/fixtures/pdf-smoke.html` → `build/artifact…`: 1 page A4, 54 KB, pypdf extracts all Chinese.
- Real UI flow: analyze → 简历 PDF page → export downloads `陈小明_简历.pdf`, 1 page, 44 KB, contact chips and skills extracted, no `⛝`
- `npm run verify:pdf` is self-contained (starts its own static server + Chromium).
- `npm run verify:app` needs the FastAPI server on `BASE_URL`.
- Chromium used: the shared `Easy-Job-Tutor/.pw-browsers/chromium-1228` (via `playwright-core` 1.61.1); override with `PDF_CHROMIUM_PATH`.

## Errors Encountered
- esbuild rejected the browser `target` array as unsupported downleveling; fixed by using `target: "es2020"`.
- Playwright 1.62 wanted chromium-1234 while only 1228 was cached; pinned `playwright-core@1.61.1` and reused 1228.
- Frontend PDF with Chinese requires an embedded font; solved with `@hmfw/html-to-pdf` + fontTools subset (GB2312 + Latin + symbols).

## Status
**Currently in Phase 6** — docs updated, running the final verification and committing.
