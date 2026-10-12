import unittest

from src import classification
from src import normalization
from src import profiles


class TestAutomatonSpecification(unittest.TestCase):

    def test_the_five_components_are_present(self):
        spec = classification.automaton_specification("FULL_STACK_DEVELOPER")
        for component in ["states", "alphabet", "transitions",
                          "initial_state", "final_states"]:
            self.assertIn(component, spec)

    def test_initial_and_final_states_belong_to_the_set_of_states(self):
        for profile_name in profiles.profile_names():
            spec = classification.automaton_specification(profile_name)
            self.assertIn(spec["initial_state"], spec["states"])
            for state in spec["final_states"]:
                self.assertIn(state, spec["states"])

    def test_final_states_are_not_empty(self):
        for profile_name in profiles.profile_names():
            spec = classification.automaton_specification(profile_name)
            self.assertTrue(spec["final_states"])

    def test_one_state_more_than_the_number_of_stages(self):
        for profile_name in profiles.profile_names():
            spec = classification.automaton_specification(profile_name)
            self.assertEqual(len(spec["states"]),
                             len(profiles.stages_of(profile_name)) + 1)

    def test_transition_relation_is_partial(self):
        spec = classification.automaton_specification("FULL_STACK_DEVELOPER")
        defined = {(source, symbol)
                   for source, symbol, _ in spec["transitions"]}
        total = len(spec["states"]) * len(spec["alphabet"])
        self.assertLess(len(defined), total)


class TestAutomatonType(unittest.TestCase):

    def test_profiles_with_an_optional_stage_use_lambda(self):
        self.assertEqual(
            classification.automaton_type("FULL_STACK_DEVELOPER"),
            "NFA-λ")
        self.assertEqual(
            classification.automaton_type("MACHINE_LEARNING_ENGINEER"),
            "NFA-λ")

    def test_profiles_without_optional_stages_have_no_lambda(self):
        self.assertEqual(classification.automaton_type("MOBILE_DEVELOPER"),
                         "NFA")
        self.assertEqual(classification.automaton_type("DATA_ENGINEER"), "NFA")


class TestAcceptance(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.automata = classification.build_all_automata()

    def accepts(self, profile_name, sequence):
        return classification.accepts(profile_name, sequence, self.automata)

    def test_example_of_the_assignment_is_accepted(self):
        self.assertTrue(self.accepts(
            "MACHINE_LEARNING_ENGINEER",
            ["PYTHON", "PANDAS", "TENSORFLOW", "POSTGRESQL", "GIT"]))

    def test_full_stack_sequence_of_the_assignment_is_accepted(self):
        self.assertTrue(self.accepts(
            "FULL_STACK_DEVELOPER",
            ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]))

    def test_optional_stage_may_also_be_present(self):
        self.assertTrue(self.accepts(
            "FULL_STACK_DEVELOPER",
            ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "REST_API",
             "GIT"]))

    def test_a_missing_required_stage_is_rejected(self):
        self.assertFalse(self.accepts(
            "FULL_STACK_DEVELOPER",
            ["JAVASCRIPT", "REACT", "NODE_JS", "GIT"]))

    def test_the_empty_sequence_is_rejected(self):
        for profile_name in profiles.profile_names():
            self.assertFalse(self.accepts(profile_name, []))

    def test_a_symbol_out_of_order_is_rejected(self):
        self.assertFalse(self.accepts(
            "FULL_STACK_DEVELOPER",
            ["GIT", "JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL"]))


class TestClassify(unittest.TestCase):

    def classify_skills(self, raw_skills):
        canonical, _ = normalization.normalize(raw_skills)
        return classification.classify(canonical)

    def test_wednesday_addams_is_a_full_stack_developer(self):
        results = self.classify_skills(
            ["JS", "React.js", "NodeJS", "Postgres", "Git"])
        self.assertEqual(classification.accepted_profiles(results),
                         ["FULL_STACK_DEVELOPER"])

    def test_mary_jane_watson_is_a_machine_learning_engineer(self):
        results = self.classify_skills(
            ["Python", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "SQL",
             "Git"])
        self.assertIn("MACHINE_LEARNING_ENGINEER",
                      classification.accepted_profiles(results))

    def test_a_mobile_developer_resume(self):
        results = self.classify_skills(
            ["Kotlin", "Android SDK", "Room", "REST APIs", "Git"])
        self.assertIn("MOBILE_DEVELOPER",
                      classification.accepted_profiles(results))

    def test_a_data_engineer_resume(self):
        results = self.classify_skills(
            ["Python", "Apache Spark", "Airflow", "BigQuery", "Git"])
        self.assertIn("DATA_ENGINEER",
                      classification.accepted_profiles(results))

    def test_a_resume_that_satisfies_no_profile(self):
        results = self.classify_skills(["Python", "Git"])
        self.assertEqual(classification.accepted_profiles(results), [])

    def test_the_four_profiles_are_always_evaluated(self):
        results = self.classify_skills(["Git"])
        self.assertEqual([item["profile"] for item in results],
                         profiles.profile_names())

    def test_missing_stages_are_reported_on_rejection(self):
        results = self.classify_skills(["Python", "Git"])
        for item in results:
            if item["verdict"] == "REJECTED":
                self.assertTrue(item["missing"])


if __name__ == "__main__":
    unittest.main()