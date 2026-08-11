import unittest

from api.matcher import analyze


class MatcherTests(unittest.TestCase):
    def test_not_developed_cannot_create_coverage_or_rewrite(self):
        result = analyze(
            "We need Python experience.",
            "I have not developed Python applications.",
            role="ai_agent",
        )

        self.assertEqual(result["keyword_coverage"], 0)
        self.assertNotIn("Python", result["matched_skills"])
        self.assertEqual(result["resume_optimization"]["bullet_rewrites"], [])
        self.assertEqual(
            result["fact_ledger"][0]["evidence_reason"],
            "explicit_negation",
        )

    def test_chinese_did_not_use_cannot_create_coverage_or_rewrite(self):
        result = analyze(
            "We need Python experience.",
            "我没有使用 Python 开发服务。",
            role="ai_agent",
        )

        self.assertEqual(result["keyword_coverage"], 0)
        self.assertNotIn("Python", result["matched_skills"])
        self.assertEqual(result["resume_optimization"]["bullet_rewrites"], [])
        self.assertEqual(
            result["fact_ledger"][0]["evidence_reason"],
            "explicit_negation",
        )

    def test_later_java_negation_keeps_python_coverage_and_rewrite(self):
        result = analyze(
            "We need Python experience.",
            "Developed Python services, never used Java.",
            role="ai_agent",
        )

        self.assertEqual(result["keyword_coverage"], 100)
        self.assertIn("Python", result["matched_skills"])
        self.assertEqual(len(result["resume_optimization"]["bullet_rewrites"]), 1)

    def test_unpunctuated_java_coordination_cannot_create_python_coverage_or_rewrite(self):
        result = analyze(
            "We need Python experience.",
            "Never used Java and developed Python services.",
            role="ai_agent",
        )

        self.assertEqual(result["keyword_coverage"], 0)
        self.assertNotIn("Python", result["matched_skills"])
        self.assertEqual(result["resume_optimization"]["bullet_rewrites"], [])
        self.assertEqual(
            result["fact_ledger"][0]["evidence_reason"],
            "explicit_negation",
        )

    def test_poetry_coordination_cannot_create_rag_coverage_or_rewrite(self):
        result = analyze(
            "We need RAG experience.",
            "Never used poetry and developed RAG applications.",
            role="ai_agent",
        )

        self.assertEqual(result["keyword_coverage"], 0)
        self.assertNotIn("RAG 检索增强", result["matched_skills"])
        self.assertEqual(result["resume_optimization"]["bullet_rewrites"], [])
        self.assertEqual(
            result["fact_ledger"][0]["evidence_reason"],
            "explicit_negation",
        )

    def test_builtin_node_alias_coordination_cannot_create_coverage_or_rewrite(self):
        result = analyze(
            "We need Node.js experience.",
            "Never used Node and developed Node.js services.",
            role="ai_agent",
        )

        self.assertEqual(result["keyword_coverage"], 0)
        self.assertNotIn("前端/TS 基础", result["matched_skills"])
        self.assertEqual(result["resume_optimization"]["bullet_rewrites"], [])
        self.assertEqual(result["fact_ledger"][0]["evidence_status"], "not_found")
        self.assertEqual(
            result["fact_ledger"][0]["evidence_reason"],
            "explicit_negation",
        )

    def test_builtin_node_action_after_dot_cannot_create_coverage_or_rewrite(self):
        result = analyze(
            "We need Node.js experience.",
            "Never used Node and developed Node.js and deployed services.",
            role="ai_agent",
        )

        self.assertEqual(result["keyword_coverage"], 0)
        self.assertNotIn("前端/TS 基础", result["matched_skills"])
        self.assertEqual(result["resume_optimization"]["bullet_rewrites"], [])
        self.assertEqual(result["fact_ledger"][0]["evidence_status"], "not_found")
        self.assertEqual(
            result["fact_ledger"][0]["evidence_reason"],
            "explicit_negation",
        )

    def test_real_period_allows_new_positive_node_statement(self):
        result = analyze(
            "We need Node.js experience.",
            "Never used Node. Developed Node.js services.",
            role="ai_agent",
        )

        self.assertEqual(result["keyword_coverage"], 100)
        self.assertIn("前端/TS 基础", result["matched_skills"])
        self.assertEqual(len(result["resume_optimization"]["bullet_rewrites"]), 1)
        self.assertEqual(result["fact_ledger"][0]["evidence_status"], "evidenced")
        self.assertEqual(
            result["fact_ledger"][0]["evidence_reason"],
            "action_context",
        )

    def test_kubernetes_alias_coordination_cannot_create_coverage_or_rewrite(self):
        result = analyze(
            "We need Kubernetes experience.",
            "Never used k8s and developed Kubernetes services.",
            role="ai_agent",
        )

        self.assertEqual(result["keyword_coverage"], 0)
        self.assertNotIn("部署/推理优化", result["matched_skills"])
        self.assertEqual(result["resume_optimization"]["bullet_rewrites"], [])
        self.assertEqual(
            result["fact_ledger"][0]["evidence_reason"],
            "explicit_negation",
        )

    def test_decorated_current_skill_cannot_create_coverage_or_rewrite(self):
        resumes = (
            "Never used 'Python' and developed Python services.",
            'Never used "Python" and developed Python services.',
            "Never used (Python) and developed Python services.",
            "Never used Python® and developed Python services.",
        )

        for resume in resumes:
            with self.subTest(resume=resume):
                result = analyze(
                    "We need Python experience.",
                    resume,
                    role="ai_agent",
                )

                self.assertEqual(result["keyword_coverage"], 0)
                self.assertNotIn("Python", result["matched_skills"])
                self.assertEqual(
                    result["resume_optimization"]["bullet_rewrites"],
                    [],
                )
                self.assertEqual(
                    result["fact_ledger"][0]["evidence_reason"],
                    "explicit_negation",
                )

    def test_generic_tool_use_object_cannot_create_coverage_or_rewrite(self):
        result = analyze(
            "We need Python experience.",
            "Never used tutorials and developed Python applications.",
            role="ai_agent",
        )

        self.assertEqual(result["keyword_coverage"], 0)
        self.assertNotIn("Python", result["matched_skills"])
        self.assertEqual(result["resume_optimization"]["bullet_rewrites"], [])
        self.assertEqual(
            result["fact_ledger"][0]["evidence_reason"],
            "explicit_negation",
        )

    def test_shared_negation_cannot_create_python_coverage_or_rewrite(self):
        result = analyze(
            "We need Python experience.",
            "I never designed web apps and developed Python applications.",
            role="ai_agent",
        )

        self.assertEqual(result["keyword_coverage"], 0)
        self.assertNotIn("Python", result["matched_skills"])
        self.assertEqual(result["resume_optimization"]["bullet_rewrites"], [])
        self.assertEqual(
            result["fact_ledger"][0]["evidence_reason"],
            "explicit_negation",
        )

    def test_capitalized_generic_object_cannot_create_coverage_or_rewrite(self):
        result = analyze(
            "We need Python experience.",
            "I never designed APIs and developed Python applications.",
            role="ai_agent",
        )

        self.assertEqual(result["keyword_coverage"], 0)
        self.assertNotIn("Python", result["matched_skills"])
        self.assertEqual(result["resume_optimization"]["bullet_rewrites"], [])
        self.assertEqual(
            result["fact_ledger"][0]["evidence_reason"],
            "explicit_negation",
        )

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
