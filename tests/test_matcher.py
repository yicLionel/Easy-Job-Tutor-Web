import unittest

from api.matcher import analyze


class MatcherTests(unittest.TestCase):
    def test_negated_requirement_cannot_have_complete_keyword_coverage(self):
        result = analyze(
            "We need Python experience.",
            "I have no Python experience and never used it in a project.",
            role="ai_agent",
        )

        self.assertNotEqual(result["keyword_coverage"], 100)
        self.assertNotIn("Python", result["matched_skills"])
        self.assertEqual(result["resume_optimization"]["bullet_rewrites"], [])
        ledger = result["fact_ledger"][0]
        self.assertEqual(ledger["status"], "model_inference")
        self.assertEqual(ledger["evidence_status"], "not_found")
        self.assertEqual(ledger["evidence_reason"], "explicit_negation")
        self.assertEqual(ledger["evidence_source"], [
            "I have no Python experience and never used it in a project."
        ])

    def test_keyword_stuffing_cannot_have_complete_keyword_coverage(self):
        result = analyze(
            "We need Python experience.",
            "Skills: Python, py, pandas, numpy, asyncio, pytest, poetry, pip.",
            role="ai_agent",
        )

        self.assertNotEqual(result["keyword_coverage"], 100)
        self.assertNotIn("Python", result["matched_skills"])
        self.assertEqual(result["resume_optimization"]["bullet_rewrites"], [])
        ledger = result["fact_ledger"][0]
        self.assertEqual(ledger["status"], "pending_confirmation")
        self.assertEqual(ledger["evidence_status"], "uncertain")
        self.assertEqual(
            ledger["evidence_reason"],
            "keyword_without_experience_context",
        )

    def test_complete_analysis_uses_skills_found_in_the_jd(self):
        result = analyze(
            "We need Python and RAG experience.",
            "Built a Python service for internal data processing.",
            role="ai_agent",
        )

        self.assertEqual(result["target_skill_count"], 2)
        self.assertIn("Python", result["matched_skills"])
        self.assertIn("rag", [keyword.lower() for keyword in result["resume_optimization"]["missing_keywords"]])
        self.assertNotIn("产品原型", [gap["label"] for gap in result["gaps"]])

    def test_optimization_keeps_original_text_and_marks_draft_as_pending(self):
        result = analyze(
            "We need Python experience.",
            "Built a Python service for internal data processing.",
            role="ai_agent",
        )

        rewrite = result["resume_optimization"]["bullet_rewrites"][0]
        self.assertIn("Built a Python service", rewrite["source"])
        self.assertIn("待确认", rewrite["suggested_bullet"])
        self.assertEqual(rewrite["fact_status"], "pending_confirmation")
        self.assertIn("真实数据", rewrite["quantification_prompt"])


if __name__ == "__main__":
    unittest.main()
