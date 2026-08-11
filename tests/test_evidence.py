import unittest

from api.evidence import classify_skill_evidence


PYTHON = {
    "label": "Python",
    "keywords": ["python", "py"],
    "importance": 5,
    "dim": "核心技能",
}


class EvidenceTests(unittest.TestCase):
    def test_explicit_negation_is_not_positive_evidence(self):
        match = classify_skill_evidence(
            PYTHON,
            "I have no Python experience and never used it in a project.",
        )

        self.assertEqual(match.status, "not_found")
        self.assertEqual(match.reason, "explicit_negation")

    def test_distant_negation_in_same_clause_is_not_positive_evidence(self):
        match = classify_skill_evidence(
            PYTHON,
            "I have never had an opportunity to develop production systems using Python.",
        )

        self.assertEqual(match.status, "not_found")
        self.assertEqual(match.reason, "explicit_negation")

    def test_keyword_list_without_action_context_is_uncertain(self):
        match = classify_skill_evidence(PYTHON, "Skills: Python, RAG, Agent")

        self.assertEqual(match.status, "uncertain")

    def test_project_action_with_keyword_is_evidenced(self):
        match = classify_skill_evidence(
            PYTHON,
            "项目经验：使用 Python 开发 FastAPI 服务并部署上线。",
        )

        self.assertEqual(match.status, "evidenced")
        self.assertIn("使用 Python 开发", match.evidence[0])

    def test_short_latin_keyword_uses_word_boundaries(self):
        ai_skill = {**PYTHON, "label": "AI", "keywords": ["ai"]}

        match = classify_skill_evidence(
            ai_skill,
            "Email: candidate@example.com. I maintain data pipelines.",
        )

        self.assertEqual(match.status, "not_found")


if __name__ == "__main__":
    unittest.main()
