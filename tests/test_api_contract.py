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
        self.assertEqual(legacy.headers.get("Deprecation"), "true")
        self.assertEqual(set(legacy.json()), SUCCESS_KEYS)
        self.assertEqual(set(legacy.json()), set(versioned.json()))
        self.assertEqual(
            set(legacy.json()["coverage_summary"]),
            set(versioned.json()["coverage_summary"]),
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
