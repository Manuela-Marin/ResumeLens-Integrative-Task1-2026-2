from .. import profiles
from .transducers import build_all_transducers


def normalize_one(raw_skill, transducers=None):
    """Translate one raw skill into its canonical form."""
    if transducers is None:
        transducers = build_all_transducers()

    symbols = list(raw_skill.strip())
    for category in profiles.category_names():
        outputs = list(transducers[category].translate(symbols))
        if outputs:
            # Every accepted branch emits exactly one canonical form.
            return "".join(outputs[0])
    return None


def normalize(raw_skills, transducers=None):
    """Translate a list of raw skills into their canonical forms."""
    if transducers is None:
        transducers = build_all_transducers()

    canonical = []
    unknown = []
    for raw_skill in raw_skills:
        translated = normalize_one(raw_skill, transducers)
        if translated is None:
            unknown.append(raw_skill)
        elif translated not in canonical:
            canonical.append(translated)
    return canonical, unknown


def canonical_order(canonical_skills, profile_name):
    """Sort canonical qualifications in the order defined by a profile."""
    present = set(canonical_skills)
    ordered = []
    for stage in profiles.stages_of(profile_name):
        for alternative in stage["alternatives"]:
            if alternative in present:
                ordered.append(alternative)
                break
    return ordered