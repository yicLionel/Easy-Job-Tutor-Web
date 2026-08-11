import unittest

from api.matcher import analyze


class MatcherTests(unittest.TestCase):
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
