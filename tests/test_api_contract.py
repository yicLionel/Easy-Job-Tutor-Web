import inspect
import re
import unittest

from fastapi.testclient import TestClient

from api import matcher
from api.knowledge import ROLES
from api.main import create_app


SUCCESS_KEYS = {
    "ok",
    "analysis_id",
    "algorithm_version",
    "knowledge_base_version",
    "role",
    "coverage_summary",
    "requirements",
    "rewrite_suggestions",
    "warnings",
}
REQUIREMENT_KEYS = {
    "requirement_id",
    "label",
    "priority",
    "jd_evidence",
    "resume_status",
    "resume_evidence",
    "reason",
}
SUGGESTION_KEYS = {
    "suggestion_id",
    "source",
    "suggested",
    "requirement_ids",
    "fact_status",
    "pending_fields",
    "default_export",
}


class AnalysisContractTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(create_app(serve_static=False))

    def _post_success_input(self, path: str = "/api/v1/analyses"):
        return self.client.post(
            path,
            data={
                "jd": "We require Python and RAG experience in deployed projects. " * 2,
                "role": "ai_agent",
                "privacy_consent_version": "2026-08-11",
            },
            files={
                "resume": (
                    "resume.txt",
                    "项目经验：使用 Python 开发并部署数据服务。",
                    "text/plain",
                ),
            },
        )

    def _analyze(self, jd: str, resume: str, role: str | None = None):
        self.assertTrue(
            hasattr(matcher, "analyze_public_beta"),
            "analyze_public_beta must provide the versioned matcher contract",
        )
        return matcher.analyze_public_beta(
            jd,
            resume,
            analysis_id="f" * 32,
            role=role,
        )

    def test_create_app_accepts_explicit_static_setting(self):
        self.assertIn("serve_static", inspect.signature(create_app).parameters)

    def test_short_jd_returns_structured_400(self):
        response = self.client.post(
            "/api/v1/analyses",
            data={
                "jd": "too short",
                "privacy_consent_version": "2026-08-11",
            },
        )

        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertEqual(
            set(body),
            {
                "ok",
                "error_code",
                "message",
                "request_id",
                "retryable",
                "supported_action",
            },
        )
        self.assertFalse(body["ok"])
        self.assertEqual(body["error_code"], "JD_TOO_SHORT")
        self.assertTrue(body["request_id"])

    def test_privacy_consent_mismatch_returns_structured_400(self):
        response = self.client.post(
            "/api/v1/analyses",
            data={
                "jd": "We require Python experience for deployed internal services. " * 2,
                "role": "ai_agent",
                "privacy_consent_version": "older-version",
            },
            files={"resume": ("resume.txt", "Built a Python service.", "text/plain")},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error_code"],
            "PRIVACY_CONSENT_REQUIRED",
        )

    def test_success_has_exact_versioned_schema(self):
        response = self._post_success_input()

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(set(body), SUCCESS_KEYS)
        self.assertRegex(body["analysis_id"], r"^[a-f0-9]{32}$")
        self.assertEqual(body["algorithm_version"], "evidence-v1")
        self.assertEqual(body["knowledge_base_version"], "2026-08-11")
        self.assertEqual(
            set(body["role"]),
            {"id", "label", "confidence"},
        )
        self.assertEqual(body["role"]["id"], "ai_agent")
        self.assertEqual(body["role"]["confidence"], 1.0)
        self.assertEqual(
            set(body["coverage_summary"]),
            {
                "known_requirement_count",
                "unknown_requirement_count",
                "evidenced_count",
                "uncertain_count",
                "missing_evidence_count",
                "keyword_coverage",
            },
        )
        self.assertEqual(
            {item["requirement_id"] for item in body["requirements"]},
            {"aa_py", "aa_rag"},
        )
        for requirement in body["requirements"]:
            self.assertEqual(set(requirement), REQUIREMENT_KEYS)

    def test_legacy_route_sets_deprecation_header_and_uses_same_schema(self):
        versioned = self._post_success_input()
        legacy = self._post_success_input("/api/analyze")

        self.assertEqual(versioned.status_code, 200)
        self.assertEqual(legacy.status_code, 200)
        self.assertIsNone(versioned.headers.get("Deprecation"))
        self.assertEqual(legacy.headers.get("Deprecation"), "true")
        self.assertEqual(set(legacy.json()), SUCCESS_KEYS)
        self.assertEqual(set(legacy.json()), set(versioned.json()))
        self.assertEqual(
            set(legacy.json()["coverage_summary"]),
            set(versioned.json()["coverage_summary"]),
        )

    def test_legacy_route_sets_deprecation_header_on_api_error(self):
        data = {
            "jd": "too short",
            "privacy_consent_version": "2026-08-11",
        }
        versioned = self.client.post("/api/v1/analyses", data=data)
        legacy = self.client.post("/api/analyze", data=data)

        self.assertEqual(versioned.status_code, 400)
        self.assertEqual(legacy.status_code, 400)
        self.assertIsNone(versioned.headers.get("Deprecation"))
        self.assertEqual(legacy.headers.get("Deprecation"), "true")
        versioned_body = versioned.json()
        legacy_body = legacy.json()
        self.assertEqual(set(legacy_body), set(versioned_body))
        for key in set(legacy_body) - {"request_id"}:
            self.assertEqual(legacy_body[key], versioned_body[key])
        self.assertTrue(versioned_body["request_id"])
        self.assertTrue(legacy_body["request_id"])
        self.assertEqual(legacy_body["error_code"], "JD_TOO_SHORT")

    def test_legacy_route_sets_deprecation_header_on_framework_422(self):
        data = {
            "jd": "Python experience is required for deployed internal services. " * 2,
            "privacy_consent_version": "2026-08-11",
        }
        malformed_resume = {"resume": (None, "not-an-upload")}

        versioned = self.client.post(
            "/api/v1/analyses",
            data=data,
            files=malformed_resume,
        )
        legacy = self.client.post(
            "/api/analyze",
            data=data,
            files=malformed_resume,
        )

        self.assertEqual(versioned.status_code, 422)
        self.assertEqual(legacy.status_code, 422)
        self.assertIsNone(versioned.headers.get("Deprecation"))
        self.assertEqual(legacy.headers.get("Deprecation"), "true")
        versioned_body = versioned.json()
        legacy_body = legacy.json()
        self.assertEqual(set(legacy_body), set(versioned_body))
        for key in set(legacy_body) - {"request_id"}:
            self.assertEqual(legacy_body[key], versioned_body[key])
        self.assertEqual(versioned_body["error_code"], "REQUEST_VALIDATION_FAILED")
        self.assertEqual(
            versioned_body["request_id"],
            versioned.headers["x-request-id"],
        )
        self.assertEqual(
            legacy_body["request_id"],
            legacy.headers["x-request-id"],
        )

    def test_unknown_only_jd_has_null_coverage_warning_and_visible_lines(self):
        result = self._analyze(
            "- 必须掌握火星岩芯封装规程并独立完成样品分级。\n"
            "- 需要维护月面尘埃治理台账并定期提交结果说明。",
            "项目经历：整理本地档案并完成交接。",
        )

        summary = result["coverage_summary"]
        self.assertEqual(summary["known_requirement_count"], 0)
        self.assertEqual(summary["unknown_requirement_count"], 2)
        self.assertIsNone(summary["keyword_coverage"])
        self.assertEqual(result["warnings"], ["KNOWN_REQUIREMENT_COVERAGE_LOW"])
        self.assertEqual(
            [item["jd_evidence"] for item in result["requirements"]],
            [
                "必须掌握火星岩芯封装规程并独立完成样品分级",
                "需要维护月面尘埃治理台账并定期提交结果说明",
            ],
        )
        self.assertTrue(
            all(item["priority"] == "unknown" for item in result["requirements"])
        )

    def test_unknown_requirement_id_is_stable_and_content_derived(self):
        first = self._analyze(
            "- 必须掌握火星岩芯封装规程并独立完成样品分级。",
            "整理本地档案并完成交接。",
        )
        second = self._analyze(
            "必须掌握火星岩芯封装规程并独立完成样品分级。",
            "另一份没有关联词汇的简历内容。",
        )

        first_id = first["requirements"][0]["requirement_id"]
        self.assertEqual(first_id, "unknown-df8694329713")
        self.assertEqual(second["requirements"][0]["requirement_id"], first_id)

    def test_normalized_duplicate_unknowns_emit_one_first_seen_requirement(self):
        result = self._analyze(
            "MUST own Martian sample custody.\n"
            "must   own Martian sample custody.",
            "Prepared unrelated project records.",
            role="ai_agent",
        )

        self.assertEqual(result["coverage_summary"]["known_requirement_count"], 0)
        self.assertEqual(result["coverage_summary"]["unknown_requirement_count"], 1)
        self.assertEqual(len(result["requirements"]), 1)
        self.assertEqual(
            result["requirements"][0]["requirement_id"],
            "unknown-b1cea9fe937a",
        )
        self.assertEqual(
            result["requirements"][0]["jd_evidence"],
            "MUST own Martian sample custody",
        )

    def test_normalized_unknown_dedup_preserves_mixed_known_counts(self):
        result = self._analyze(
            "Python experience is required.\n"
            "MUST own Martian sample custody.\n"
            "must   own Martian sample custody.",
            "Built a Python service for internal teams.",
            role="ai_agent",
        )

        self.assertEqual(result["coverage_summary"]["known_requirement_count"], 1)
        self.assertEqual(result["coverage_summary"]["unknown_requirement_count"], 1)
        self.assertEqual(
            [item["requirement_id"] for item in result["requirements"]],
            ["aa_py", "unknown-b1cea9fe937a"],
        )
        self.assertEqual(
            result["requirements"][1]["jd_evidence"],
            "MUST own Martian sample custody",
        )

    def test_unknown_cap_applies_after_normalized_deduplication(self):
        statements = [
            "MUST own Martian sample custody.",
            "must   own Martian sample custody.",
            *[
                f"MUST own Martian sample custody zone {index}."
                for index in range(1, 13)
            ],
        ]

        result = self._analyze(
            "\n".join(statements),
            "Prepared unrelated project records.",
            role="ai_agent",
        )
        requirement_ids = [
            item["requirement_id"] for item in result["requirements"]
        ]

        self.assertEqual(len(requirement_ids), 12)
        self.assertEqual(len(set(requirement_ids)), 12)
        self.assertEqual(
            result["requirements"][0]["jd_evidence"],
            "MUST own Martian sample custody",
        )

    def test_boundary_aware_requirement_discovery_avoids_substring_hits(self):
        self.assertTrue(
            hasattr(matcher, "build_requirements"),
            "build_requirements must discover JD evidence",
        )

        requirements = matcher.build_requirements(
            "Storage stewardship and orbital custody are required.",
            ROLES["ai_agent"]["skills"],
            "Built an unrelated internal service.",
        )

        self.assertNotIn(
            "aa_rag",
            {item["requirement_id"] for item in requirements},
        )
        self.assertEqual(len(requirements), 1)
        self.assertEqual(requirements[0]["priority"], "unknown")

    def test_reactive_does_not_discover_react_requirements_or_rewrites(self):
        result = self._analyze(
            "Reactive platform ownership is required for this role.",
            "Developed React services for production.",
            role="ai_agent",
        )

        summary = result["coverage_summary"]
        self.assertEqual(summary["known_requirement_count"], 0)
        self.assertEqual(summary["unknown_requirement_count"], 1)
        self.assertIsNone(summary["keyword_coverage"])
        self.assertEqual(result["rewrite_suggestions"], [])
        self.assertTrue(
            {"aa_js", "aa_agent", "aa_fe"}.isdisjoint(
                item["requirement_id"] for item in result["requirements"]
            )
        )

    def test_interest_does_not_discover_rest_requirement_or_rewrite(self):
        result = self._analyze(
            "Interest in distributed service ownership is required.",
            "Developed REST services for internal teams.",
            role="ai_agent",
        )

        summary = result["coverage_summary"]
        self.assertEqual(summary["known_requirement_count"], 0)
        self.assertEqual(summary["unknown_requirement_count"], 1)
        self.assertIsNone(summary["keyword_coverage"])
        self.assertEqual(result["rewrite_suggestions"], [])
        self.assertNotIn(
            "aa_backend",
            {item["requirement_id"] for item in result["requirements"]},
        )

    def test_symbol_bearing_and_cjk_keywords_remain_discoverable(self):
        cases = (
            (
                "Node.js experience is required for this role.",
                "Developed Node.js services for internal teams.",
                "ai_agent",
                {"aa_js"},
            ),
            (
                "CI/CD experience is required for this role.",
                "Implemented CI/CD pipelines for internal teams.",
                "ai_agent",
                {"aa_test", "aa_git"},
            ),
            (
                "Fine-tune workflow experience is preferred for this role.",
                "Developed fine-tune workflows for internal teams.",
                "ai_agent",
                {"aa_ft"},
            ),
            (
                "A/B testing experience is preferred for this role.",
                "Designed A/B tests for product experiments.",
                "ai_product",
                {"ap_data", "ap_ab"},
            ),
            (
                "需要微调工作流经验并负责模型训练。",
                "使用微调完成模型训练与内部交付。",
                "ai_agent",
                {"aa_ft"},
            ),
        )

        for jd_text, resume_text, role, expected_ids in cases:
            with self.subTest(jd_text=jd_text):
                result = self._analyze(jd_text, resume_text, role=role)
                requirement_ids = {
                    item["requirement_id"] for item in result["requirements"]
                }
                self.assertTrue(expected_ids.issubset(requirement_ids))

    def test_preferred_language_marks_known_requirement_preferred(self):
        self.assertTrue(hasattr(matcher, "build_requirements"))

        requirements = matcher.build_requirements(
            "Nice to have: Python experience for platform automation.",
            ROLES["ai_agent"]["skills"],
            "Built a Python service for internal teams.",
        )
        python_requirement = next(
            item for item in requirements if item["requirement_id"] == "aa_py"
        )

        self.assertEqual(python_requirement["priority"], "preferred")
        self.assertEqual(
            python_requirement["jd_evidence"],
            "Nice to have: Python experience for platform automation",
        )

    def test_rewrite_suggestion_never_invents_a_numeric_metric(self):
        source = "Built a Python service for internal document processing."
        result = self._analyze(
            "We require Python experience for resilient internal platform delivery.",
            source,
            role="ai_agent",
        )

        self.assertTrue(result["rewrite_suggestions"])
        suggestion = result["rewrite_suggestions"][0]
        self.assertEqual(set(suggestion), SUGGESTION_KEYS)
        self.assertEqual(suggestion["suggestion_id"], "rw-001")
        self.assertEqual(suggestion["source"], source)
        self.assertIsNone(re.search(r"\d", suggestion["suggested"]))
        self.assertEqual(suggestion["fact_status"], "pending_confirmation")
        self.assertEqual(
            suggestion["pending_fields"],
            ["metric", "time_range", "personal_contribution"],
        )
        self.assertFalse(suggestion["default_export"])


if __name__ == "__main__":
    unittest.main()
