import unittest

from api.evidence import classify_skill_evidence


PYTHON = {
    "label": "Python",
    "keywords": ["python", "py"],
    "importance": 5,
    "dim": "核心技能",
}
JAVA = {
    "label": "Java",
    "keywords": ["java"],
    "importance": 5,
    "dim": "核心技能",
}


class EvidenceTests(unittest.TestCase):
    def test_not_developed_is_explicit_negation(self):
        match = classify_skill_evidence(
            PYTHON,
            "I have not developed Python applications.",
        )

        self.assertEqual(match.status, "not_found")
        self.assertEqual(match.reason, "explicit_negation")

    def test_post_keyword_not_construction_is_explicit_negation(self):
        match = classify_skill_evidence(
            PYTHON,
            "Python applications were not developed.",
        )

        self.assertEqual(match.status, "not_found")
        self.assertEqual(match.reason, "explicit_negation")

    def test_chinese_did_not_use_is_explicit_negation(self):
        match = classify_skill_evidence(
            PYTHON,
            "我没有使用 Python 开发服务。",
        )

        self.assertEqual(match.status, "not_found")
        self.assertEqual(match.reason, "explicit_negation")

    def test_later_java_negation_does_not_suppress_python_evidence(self):
        text = "Developed Python services, never used Java."

        python_match = classify_skill_evidence(PYTHON, text)
        java_match = classify_skill_evidence(JAVA, text)

        self.assertEqual(python_match.status, "evidenced")
        self.assertEqual(python_match.reason, "action_context")
        self.assertEqual(java_match.status, "not_found")
        self.assertEqual(java_match.reason, "explicit_negation")

    def test_coordinated_positive_action_resets_earlier_java_negation(self):
        text = "Never used Java and developed Python services."

        python_match = classify_skill_evidence(PYTHON, text)
        java_match = classify_skill_evidence(JAVA, text)

        self.assertEqual(python_match.status, "evidenced")
        self.assertEqual(python_match.reason, "action_context")
        self.assertEqual(java_match.status, "not_found")
        self.assertEqual(java_match.reason, "explicit_negation")

    def test_tool_use_transition_does_not_depend_on_capitalization(self):
        match = classify_skill_evidence(
            PYTHON,
            "Never used java and developed Python services.",
        )

        self.assertEqual(match.status, "evidenced")
        self.assertEqual(match.reason, "action_context")

    def test_same_skill_tool_use_chain_stays_negated(self):
        match = classify_skill_evidence(
            PYTHON,
            "Never used Python and developed Python services.",
        )

        self.assertEqual(match.status, "not_found")
        self.assertEqual(match.reason, "explicit_negation")

    def test_decorated_current_skill_tool_use_stays_negated(self):
        texts = (
            "Never used 'Python' and developed Python services.",
            'Never used "Python" and developed Python services.',
            "Never used (Python) and developed Python services.",
            "Never used Python® and developed Python services.",
        )

        for text in texts:
            with self.subTest(text=text):
                match = classify_skill_evidence(PYTHON, text)

                self.assertEqual(match.status, "not_found")
                self.assertEqual(match.reason, "explicit_negation")

    def test_generic_tool_use_object_stays_negated(self):
        match = classify_skill_evidence(
            PYTHON,
            "Never used tutorials and developed Python applications.",
        )

        self.assertEqual(match.status, "not_found")
        self.assertEqual(match.reason, "explicit_negation")

    def test_shared_negated_predicate_chain_stays_negated(self):
        match = classify_skill_evidence(
            PYTHON,
            "I never designed or developed Python applications.",
        )

        self.assertEqual(match.status, "not_found")
        self.assertEqual(match.reason, "explicit_negation")

    def test_shared_negation_with_generic_object_stays_negated(self):
        match = classify_skill_evidence(
            PYTHON,
            "I never designed web apps and developed Python applications.",
        )

        self.assertEqual(match.status, "not_found")
        self.assertEqual(match.reason, "explicit_negation")

    def test_capitalized_generic_object_stays_negated(self):
        match = classify_skill_evidence(
            PYTHON,
            "I never designed APIs and developed Python applications.",
        )

        self.assertEqual(match.status, "not_found")
        self.assertEqual(match.reason, "explicit_negation")

    def test_positive_span_after_negated_contrast_is_evidenced(self):
        match = classify_skill_evidence(
            PYTHON,
            "I have no Python experience, but developed a Python service.",
        )

        self.assertEqual(match.status, "evidenced")
        self.assertEqual(match.reason, "action_context")

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
