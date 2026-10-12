from .. import profiles
from ..normalization import canonical_order
from .automata import build_all_automata, automaton_type


def accepts(profile_name, sequence, automata=None):
    """Return True when a sequence of canonical qualifications is accepted."""
    if automata is None:
        automata = build_all_automata()
    return bool(automata[profile_name].accepts(list(sequence)))


def missing_stages(profile_name, canonical_skills):
    """Return the required stages the candidate cannot satisfy."""
    present = set(canonical_skills)
    missing = []
    for stage in profiles.stages_of(profile_name):
        if not stage["required"]:
            continue
        if not present.intersection(stage["alternatives"]):
            missing.append(stage["stage"])
    return missing


def classify(canonical_skills, automata=None):
    """Evaluate a candidate against the four profiles."""
    if automata is None:
        automata = build_all_automata()

    results = []
    for profile_name in profiles.profile_names():
        sequence = canonical_order(canonical_skills, profile_name)
        accepted = accepts(profile_name, sequence, automata)
        results.append({
            "profile": profile_name,
            "type": automaton_type(profile_name),
            "sequence": sequence,
            "verdict": "ACCEPTED" if accepted else "REJECTED",
            "missing": [] if accepted else missing_stages(profile_name,
                                                          canonical_skills),
        })
    return results


def accepted_profiles(results):
    """Return the names of the profiles accepted in a classification result."""
    return [item["profile"] for item in results
            if item["verdict"] == "ACCEPTED"]