import unittest

from src import classification
from src import dsl
from src import extraction
from src import normalization
from src import visualization
from src.visualization import html_renderer

RESUME = """Wednesday Addams
Email: wednesday.addams@example.com
Phone: 300-555-123
Location: Nevermore Academy, Jericho
Role: Student and independent investigator

Summary:
Detail-oriented developer with 3 years of experience developing web
applications.

Education:
BSc in Computer Science, Nevermore Academy, 2024

Experience:
Web Application Developer | Nevermore Academy Projects | 3 years
- Implemented backend services using Node.js.

Technical Skills:
JS, React.js, NodeJS, Postgres, Git
"""

MINIMAL = """candidate "John Smith" {
    contact {
        email john.smith@example.com
    }
    skills {
        PYTHON GIT
    }
    evaluation MACHINE_LEARNING_ENGINEER {
        pattern REJECTED
    }
}
"""


def pipeline(text):
    extracted = extraction.extract(text)
    canonical, _ = normalization.normalize(extracted["raw_skills"])
    results = classification.classify(canonical)
    return dsl.build(extracted, canonical, results)


class TestGeneratedProfileIsValid(unittest.TestCase):

    def test_the_generated_sentence_belongs_to_the_language(self):
        valid, message = dsl.is_valid(pipeline(RESUME))
        self.assertTrue(valid, message)

    def test_a_minimal_profile_is_valid(self):
        valid, message = dsl.is_valid(MINIMAL)
        self.assertTrue(valid, message)

    def test_the_model_carries_the_expected_information(self):
        model = dsl.validate(pipeline(RESUME))
        self.assertEqual(model.name, "Wednesday Addams")
        self.assertEqual(model.contact.email, "wednesday.addams@example.com")
        self.assertEqual(list(model.skills),
                         ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL",
                          "GIT"])
        self.assertEqual(len(model.evaluations), 4)

    def test_comments_are_ignored(self):
        valid, message = dsl.is_valid("// a comment\n" + MINIMAL)
        self.assertTrue(valid, message)


class TestLexicalRejection(unittest.TestCase):

    def test_a_lower_case_qualification_is_rejected(self):
        text = MINIMAL.replace("PYTHON GIT", "python GIT")
        valid, _ = dsl.is_valid(text)
        self.assertFalse(valid)

    def test_a_malformed_email_is_rejected(self):
        text = MINIMAL.replace("john.smith@example.com", "john.smith.example")
        valid, _ = dsl.is_valid(text)
        self.assertFalse(valid)

    def test_an_unknown_verdict_is_rejected(self):
        text = MINIMAL.replace("pattern REJECTED", "pattern MAYBE")
        valid, _ = dsl.is_valid(text)
        self.assertFalse(valid)

    def test_a_qualification_starting_with_an_underscore_is_rejected(self):
        text = MINIMAL.replace("PYTHON GIT", "_PYTHON GIT")
        valid, _ = dsl.is_valid(text)
        self.assertFalse(valid)


class TestSyntacticRejection(unittest.TestCase):

    def test_a_profile_without_a_skills_block_is_rejected(self):
        text = """candidate "John Smith" {
            contact { email john@example.com }
            evaluation DATA_ENGINEER { pattern REJECTED }
        }
        """
        valid, _ = dsl.is_valid(text)
        self.assertFalse(valid)

    def test_a_profile_without_any_evaluation_is_rejected(self):
        text = """candidate "John Smith" {
            contact { email john@example.com }
            skills { GIT }
        }
        """
        valid, _ = dsl.is_valid(text)
        self.assertFalse(valid)

    def test_a_profile_without_contact_is_rejected(self):
        text = """candidate "John Smith" {
            skills { GIT }
            evaluation DATA_ENGINEER { pattern REJECTED }
        }
        """
        valid, _ = dsl.is_valid(text)
        self.assertFalse(valid)

    def test_an_unclosed_block_is_rejected(self):
        valid, _ = dsl.is_valid(MINIMAL.rstrip()[:-1])
        self.assertFalse(valid)

    def test_the_empty_input_is_rejected(self):
        valid, _ = dsl.is_valid("")
        self.assertFalse(valid)


class TestVisualization(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.model = dsl.validate(pipeline(RESUME))

    def test_html_contains_the_sections_of_the_example(self):
        html = visualization.render_html(self.model)
        for fragment in ["<!DOCTYPE html>", "Wednesday Addams",
                         "Personal Information", "Profile Summary",
                         "Experience", "Normalized Technical Skills",
                         "Qualification Evaluation", "</html>"]:
            self.assertIn(fragment, html)

    def test_html_shows_the_normalized_skills(self):
        html = visualization.render_html(self.model)
        for skill in ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]:
            self.assertIn(skill, html)

    def test_html_shows_the_accepted_profile(self):
        html = visualization.render_html(self.model)
        self.assertIn("Full Stack Developer", html)
        self.assertIn("ACCEPTED", html)

    def test_markdown_is_produced(self):
        markdown = visualization.render_markdown(self.model)
        self.assertIn("# Wednesday Addams", markdown)
        self.assertIn("## Normalized Technical Skills", markdown)

    def test_html_escapes_special_characters(self):
        self.assertEqual(html_renderer._escape("<b>&\"x\""),
                         "&lt;b&gt;&amp;&quot;x&quot;")


if __name__ == "__main__":
    unittest.main()