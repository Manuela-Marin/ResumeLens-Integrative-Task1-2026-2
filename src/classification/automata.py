from pyformlang.finite_automaton import EpsilonNFA

from .. import profiles


# Symbol used by pyformlang to denote a lambda (epsilon) transition.
LAMBDA = "epsilon"


SUBSCRIPTS = "₀₁₂₃₄₅₆₇₈₉"


def _state_name(index):
    """Return the name of the state that sits after `index` stages."""
    return "q" + "".join(SUBSCRIPTS[int(digit)] for digit in str(index))


def automaton_specification(profile_name):
    """Return the formal description of the automaton of one profile."""
    pattern = profiles.stages_of(profile_name)

    states = [_state_name(index) for index in range(len(pattern) + 1)]
    alphabet = set()
    transitions = []

    for index, stage in enumerate(pattern):
        source = states[index]
        target = states[index + 1]
        for alternative in stage["alternatives"]:
            alphabet.add(alternative)
            transitions.append((source, alternative, target))
        if not stage["required"]:
            transitions.append((source, LAMBDA, target))

    return {
        "name": profile_name,
        "states": states,
        "alphabet": alphabet,
        "transitions": transitions,
        "initial_state": states[0],
        "final_states": [states[-1]],
        "stages": pattern,
    }


def automaton_type(profile_name):
    """Return the type of the automaton of a profile, as a short string."""
    specification = automaton_specification(profile_name)
    for _, symbol, _ in specification["transitions"]:
        if symbol == LAMBDA:
            return "NFA-λ"
    return "NFA"


def build_automaton(profile_name):
    """Build the pyformlang automaton of one profile."""
    specification = automaton_specification(profile_name)

    automaton = EpsilonNFA()
    for source, symbol, target in specification["transitions"]:
        automaton.add_transition(source, symbol, target)
    automaton.add_start_state(specification["initial_state"])
    for state in specification["final_states"]:
        automaton.add_final_state(state)
    return automaton


def build_all_automata():
    """Build one automaton per profile."""
    return {
        profile_name: build_automaton(profile_name)
        for profile_name in profiles.profile_names()
    }


def format_specification(profile_name):
    """Return the 5-tuple of an automaton as readable text."""
    spec = automaton_specification(profile_name)
    lines = []
    lines.append("Automaton " + spec["name"] +
                 "  M = (Q, Σ, δ, q₀, F)")
    lines.append("  Type = " + automaton_type(profile_name))
    lines.append("  Q  = {" + ", ".join(spec["states"]) + "}")
    lines.append("  Σ  = {" + ", ".join(sorted(spec["alphabet"])) + "}")
    lines.append("  q₀ = " + spec["initial_state"])
    lines.append("  F  = {" + ", ".join(spec["final_states"]) + "}")
    lines.append("  δ  : " + str(len(spec["transitions"])) +
                 " transitions")
    for source, symbol, target in spec["transitions"]:
        shown = "λ" if symbol == LAMBDA else symbol
        lines.append("    δ(" + source + ", " + shown + ") = " + target)
    lines.append("  Profile pattern:")
    for index, stage in enumerate(spec["stages"]):
        kind = "required" if stage["required"] else "optional"
        lines.append("    " + str(index + 1) + ". " + stage["stage"] +
                     " (" + kind + "): " + " | ".join(stage["alternatives"]))
    return "\n".join(lines)