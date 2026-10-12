import unittest

from src import extraction
from src.extraction import patterns as extraction_patterns

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
- Stored structured information using PostgreSQL databases.

Technical Skills:
JS, React.js, NodeJS, Postgres, Git
"""


class TestContact(unittest.TestCase):

    def test_name_is_the_first_line_of_capitalised_words(self):
        self.assertEqual(extraction.extract_contact(RESUME)["name"],
                         "Wednesday Addams")

    def test_email_is_recognised(self):
        self.assertEqual(extraction.extract_contact(RESUME)["email"],
                         "wednesday.addams@example.com")

    def test_phone_is_recognised(self):
        self.assertEqual(extraction.extract_contact(RESUME)["phone"],
                         "300-555-123")

    def test_location_and_role_are_recognised(self):
        contact = extraction.extract_contact(RESUME)
        self.assertEqual(contact["location"], "Nevermore Academy, Jericho")
        self.assertEqual(contact["role"],
                         "Student and independent investigator")

    def test_missing_fields_are_none(self):
        contact = extraction.extract_contact("John Smith\n")
        self.assertIsNone(contact["email"])
        self.assertIsNone(contact["location"])


class TestPhoneFormats(unittest.TestCase):

    def test_three_formats_of_the_lecture_exercise(self):
        for written in ["555-555-555", "555 555 555", "555555555"]:
            match = extraction_patterns.PHONE_PATTERN.search(
                "Phone: " + written)
            self.assertIsNotNone(match, written)
            self.assertEqual(match.group("phone"), written)


class TestSummary(unittest.TestCase):

    def test_summary_is_joined_into_one_line(self):
        self.assertEqual(
            extraction.extract_summary(RESUME),
            "Detail-oriented developer with 3 years of experience "
            "developing web applications.")

    def test_summary_is_none_when_absent(self):
        self.assertIsNone(extraction.extract_summary("John Smith\n"))


class TestEducation(unittest.TestCase):

    def test_one_record_is_extracted(self):
        records = extraction.extract_education(RESUME)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["degree"], "BSc")
        self.assertEqual(records[0]["field"], "Computer Science")
        self.assertEqual(records[0]["institution"], "Nevermore Academy")
        self.assertEqual(records[0]["year"], 2024)

    def test_no_record_gives_an_empty_list(self):
        self.assertEqual(extraction.extract_education("John Smith\n"), [])


class TestExperience(unittest.TestCase):

    def test_entry_and_its_responsibilities(self):
        entries = extraction.extract_experience(RESUME)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["title"], "Web Application Developer")
        self.assertEqual(entries[0]["organization"],
                         "Nevermore Academy Projects")
        self.assertEqual(entries[0]["years"], 3)
        self.assertEqual(len(entries[0]["responsibilities"]), 2)

    def test_total_years_of_experience(self):
        self.assertEqual(extraction.extract_total_experience(RESUME), 3)


class TestSkills(unittest.TestCase):

    def test_skills_are_returned_exactly_as_written(self):
        self.assertEqual(extraction.extract_skills(RESUME),
                         ["JS", "React.js", "NodeJS", "Postgres", "Git"])

    def test_stage_one_does_not_normalise(self):
        skills = extraction.extract_skills(RESUME)
        self.assertIn("JS", skills)
        self.assertNotIn("JAVASCRIPT", skills)

    def test_no_skills_section_gives_an_empty_list(self):
        self.assertEqual(extraction.extract_skills("John Smith\n"), [])


class TestExtractAll(unittest.TestCase):

    def test_every_key_is_present(self):
        data = extraction.extract(RESUME)
        for key in ["name", "email", "phone", "location", "role", "summary",
                    "education", "experience", "total_experience_years",
                    "raw_skills"]:
            self.assertIn(key, data)


if __name__ == "__main__":
    unittest.main()