# Public Beta telemetry contract

This contract is intentionally body-free. Telemetry must never contain a job
description, resume text, evidence text, suggestion or edited text, filename,
free-form feedback, URL, email address, or phone-like value. Accepted events are
written as one compact JSON log line after server-side validation. Rejected
events emit only an aggregate `telemetry_rejected` counter with a safe reason
code and `count: 1`; the rejected body and exception message are never logged.

`POST /api/v1/events` accepts an encoded body of at most 4 KiB and exactly two
top-level keys: `name` and `attributes`. Unknown attribute keys are discarded,
but a PII-like, multiline, nested, or over-64-character value rejects the whole
event before filtering.

## Event ownership

The backend is authoritative for analysis lifecycle events because it creates
the opaque analysis ID. It emits `analysis_started`, `analysis_succeeded`,
`upload_validation_failed`, and `analysis_failed`. The browser must not post
duplicates of those events.

The browser emits `page_viewed` and, only after a successful response, the
interaction events `evidence_viewed`, `suggestion_accepted`,
`suggestion_edited`, `suggestion_rejected`, `draft_exported`, and
`feedback_submitted`. Every browser interaction event reuses the returned
`analysis_id`; no identifier is derived from JD, resume, filename, or other
user input.

## Event dictionary

| Event | Owner | Allowed attributes |
|---|---|---|
| `page_viewed` | Browser | `device_category`, `referrer_category` |
| `analysis_started` | Backend | `analysis_id`, `file_type`, `file_size_bucket`, `jd_length_bucket`, `algorithm_version` |
| `upload_validation_failed` | Backend | `analysis_id`, `error_code`, `file_type`, `file_size_bucket` |
| `analysis_succeeded` | Backend | `analysis_id`, `file_type`, `processing_ms`, `algorithm_version`, `known_count`, `unknown_count`, `evidenced_count`, `uncertain_count` |
| `analysis_failed` | Backend | `analysis_id`, `error_code`, `processing_ms`, `retryable` |
| `evidence_viewed` | Browser | `analysis_id`, `requirement_id`, `resume_status` |
| `suggestion_accepted` | Browser | `analysis_id`, `suggestion_id`, `algorithm_version` |
| `suggestion_edited` | Browser | `analysis_id`, `suggestion_id`, `confirmed_pending_facts` |
| `suggestion_rejected` | Browser | `analysis_id`, `suggestion_id`, `reason_code` |
| `draft_exported` | Browser | `analysis_id`, `format`, `suggestion_count`, `pending_count` |
| `feedback_submitted` | Browser | `analysis_id`, `rating`, `reason_code` |

`analysis_id` is required on every event except `page_viewed` and must match
`^[a-f0-9]{32}$`. `requirement_id` and `suggestion_id` must match
`^[a-z0-9_-]{1,64}$`. Booleans must be JSON booleans. Counts and
`processing_ms` must be finite, non-negative JSON numbers.

## Closed enums

- `device_category`: `desktop`, `mobile`, `tablet`, `unknown`
- `referrer_category`: `direct`, `search`, `social`, `referral`, `unknown`
- `file_type`: `pdf`, `docx`, `txt`
- `file_size_bucket`: `lt_100kb`, `100kb_1mb`, `1mb_5mb`
- `jd_length_bucket`: `50_199`, `200_499`, `500_1999`, `2000_20000`
- `algorithm_version`: the configured `ALGORITHM_VERSION` only (currently `evidence-v1`)
- `resume_status`: `evidenced`, `uncertain`, `not_found`
- `format`: `markdown`
- `rating`: `helpful`, `neutral`, `unhelpful`
- `reason_code`: `not_relevant`, `not_accurate`, `clarity`, `usability`, `other`, `no_reason`
- `error_code`: `JD_TOO_SHORT`, `JD_TOO_LONG`, `FILE_TOO_LARGE`, `UNSUPPORTED_FILE_TYPE`, `FILE_MIME_MISMATCH`, `FILE_SIGNATURE_MISMATCH`, `PDF_TOO_MANY_PAGES`, `DOCX_UNCOMPRESSED_TOO_LARGE`, `DOCX_COMPRESSION_RATIO_TOO_HIGH`, `RESUME_TEXT_EMPTY`, `ANALYSIS_BUSY`, `ANALYSIS_TIMEOUT`, `EVENT_TOO_LARGE`, `INVALID_EVENT`

## Metric equations

- analysis success rate = `analysis_succeeded / analysis_started`
- effective suggestion adoption = distinct `analysis_id` with accepted, edited, or exported suggestion / distinct successful `analysis_id`
- export rate = distinct exported `analysis_id` / distinct successful `analysis_id`
- helpful rate = positive `feedback_submitted / all feedback_submitted`

Each rate view must also show its numerator, denominator, and sample size. Do
not interpret samples below 30 as a significant trend.

## Required production views

The production observability provider must save views for:

1. `analysis_started` count;
2. `analysis_succeeded` count;
3. `analysis_failed` count;
4. HTTP 5xx count and rate;
5. `processing_ms` distribution, including p95;
6. `error_code` count grouped by code.

## Required launch alerts

- `/api/health` fails twice consecutively: page the release owner.
- HTTP 5xx rate is at least 1% over five minutes, or three 5xx responses occur
  in five minutes: open rollback review.
- p95 analysis latency exceeds 12 seconds for ten minutes: start a capacity
  investigation.
- Any telemetry/PII rejection counter is above zero: disable telemetry and
  start a privacy review.
- Analysis success rate is below 98% over the gray-release window: No-Go.

## Launch verification

**Status: pending — G3 remains blocked.** This worktree has no authenticated
Vercel account/provider access, so no production view or alert has been saved,
no synthetic failure has been triggered, and no received-alert evidence exists.
These actions must not be represented as complete from repository changes.

Before G3 can pass, the release owner must configure every view and alert above
in Vercel Observability, trigger one non-sensitive synthetic failure, and record
the deployment URL, UTC timestamp, alert rule, delivery target, and received
incident/alert identifier here and in the Task 12 release runbook. If the active
Vercel plan cannot express these views or alerts, the product owner must select
and configure an external uptime/error-monitoring provider. Manual log watching
is not an acceptable substitute for public Beta.
