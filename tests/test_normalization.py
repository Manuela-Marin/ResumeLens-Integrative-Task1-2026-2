import unittest

from src import normalization
from src import profiles


class TestTransducerSpecification(unittest.TestCase):

    def test_the_seven_components_are_present(self):
        spec = normalization.transducer_specification("VERSION_CONTROL")
        for component in ["states", "input_alphabet", "output_alphabet",
                          "transitions", "initial_state", "final_states"]:
            self.assertIn(component, spec)

    def test_initial_state_belongs_to_the_set_of_states(self):
        for category in profiles.category_names():
            spec = normalization.transducer_specification(category)
            self.assertIn(spec["initial_state"], spec["states"])

    def test_final_states_are_not_empty_and_are_states(self):
        """Lecture 6-7, slide 18 requires F to be a non-empty subset of Q."""
        for category in profiles.category_names():
            spec = normalization.transducer_specification(category)
            self.assertTrue(spec["final_states"])
            self.assertTrue(spec["final_states"].issubset(spec["states"]))

    def test_output_alphabet_is_the_set_of_canonical_forms(self):
        spec = normalization.transducer_specification("FRONTEND")
        self.assertEqual(spec["output_alphabet"], {"REACT", "ANGULAR", "VUE"})

    def test_every_transition_connects_two_states(self):
        for category in profiles.category_names():
            spec = normalization.transducer_specification(category)
            for source, _, target, _ in spec["transitions"]:
                self.assertIn(source, spec["states"])
                self.assertIn(target, spec["states"])


class TestTransductions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.transducers = normalization.build_all_transducers()

    def translate(self, raw):
        return normalization.normalize_one(raw, self.transducers)

    def test_examples_of_the_assignment(self):
        expected = {
            "JS": "JAVASCRIPT",
            "Javascript": "JAVASCRIPT",
            "React.js": "REACT",
            "ReactJS": "REACT",
            "NodeJS": "NODE_JS",
            "Node.js": "NODE_JS",
            "Postgres": "POSTGRESQL",
            "PostgreSQL": "POSTGRESQL",
            "pandas": "PANDAS",
            "sklearn": "SCIKIT_LEARN",
            "scikit learn": "SCIKIT_LEARN",
            "Scikit-learn": "SCIKIT_LEARN",
            "Tensor Flow": "TENSORFLOW",
            "TensorFlow": "TENSORFLOW",
            "Py Torch": "PYTORCH",
            "PyTorch": "PYTORCH",
        }
        for raw, canonical in expected.items():
            self.assertEqual(self.translate(raw), canonical, raw)

    def test_variants_containing_a_space(self):
        self.assertEqual(self.translate("Spring Boot"), "SPRING_BOOT")
        self.assertEqual(self.translate("Apache Spark"), "SPARK")
        self.assertEqual(self.translate("Big Query"), "BIGQUERY")
        self.assertEqual(self.translate("Android SDK"), "ANDROID_SDK")

    def test_a_variant_that_is_a_prefix_of_another_variant(self):
        self.assertEqual(self.translate("Java"), "JAVA")
        self.assertEqual(self.translate("JavaScript"), "JAVASCRIPT")
        self.assertEqual(self.translate("Swift"), "SWIFT")
        self.assertEqual(self.translate("SwiftUI"), "SWIFTUI")
        self.assertEqual(self.translate("React"), "REACT")
        self.assertEqual(self.translate("React Native"), "REACT_NATIVE")
        self.assertEqual(self.translate("Room"), "ROOM")
        self.assertEqual(self.translate("Room Database"), "ROOM")

    def test_unknown_qualification_is_not_translated(self):
        self.assertIsNone(self.translate("Fortran"))
        self.assertIsNone(self.translate("COBOL"))
        self.assertIsNone(self.translate(""))


class TestNormalize(unittest.TestCase):

    def test_duplicates_are_removed_and_unknowns_reported(self):
        canonical, unknown = normalization.normalize(
            ["JS", "Javascript", "Git", "Fortran"])
        self.assertEqual(canonical, ["JAVASCRIPT", "GIT"])
        self.assertEqual(unknown, ["Fortran"])

    def test_example_of_the_assignment(self):
        canonical, unknown = normalization.normalize(
            ["JS", "React.js", "NodeJS", "Postgres", "Git"])
        self.assertEqual(
            canonical,
            ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"])
        self.assertEqual(unknown, [])


class TestCanonicalOrder(unittest.TestCase):

    def test_sequence_printed_in_the_assignment(self):
        canonical, _ = normalization.normalize(
            ["Git", "NodeJS", "JS", "Postgres", "React.js"])
        ordered = normalization.canonical_order(canonical,
                                                "FULL_STACK_DEVELOPER")
        self.assertEqual(
            ordered,
            ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"])

    def test_order_does_not_depend_on_the_order_of_the_resume(self):
        first, _ = normalization.normalize(
            ["JS", "React", "Node", "SQL", "Git"])
        second, _ = normalization.normalize(
            ["Git", "SQL", "Node", "React", "JS"])
        self.assertEqual(
            normalization.canonical_order(first, "FULL_STACK_DEVELOPER"),
            normalization.canonical_order(second, "FULL_STACK_DEVELOPER"))

    def test_one_qualification_per_stage(self):
        canonical, _ = normalization.normalize(
            ["Python", "pandas", "numpy", "sklearn", "SQL", "Git"])
        ordered = normalization.canonical_order(canonical,
                                                "MACHINE_LEARNING_ENGINEER")
        self.assertEqual(ordered.count("PANDAS") + ordered.count("NUMPY"), 1)


if __name__ == "__main__":
    unittest.main()