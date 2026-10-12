from pyformlang.fst import FST

from .. import profiles


# Symbol used by pyformlang to denote a lambda (epsilon) transition.
LAMBDA = "epsilon"

# Name of the single initial state of every transducer.
START_STATE = "q₀"


def _branch_states(variant):
    """Return the names of the states visited while reading `variant`."""
    states = [START_STATE]
    for length in range(1, len(variant) + 1):
        states.append("q_" + variant[:length])
    return states


def transducer_specification(category):
    """Return the formal description of the transducer of one category."""
    canonical_forms = profiles.QUALIFICATION_VARIANTS[category]

    states = {START_STATE}
    input_alphabet = set()
    output_alphabet = set()
    final_states = set()
    transitions = []
    seen = set()

    for canonical, variants in canonical_forms.items():
        accepting = "F_" + canonical
        final_states.add(accepting)
        states.add(accepting)
        output_alphabet.add(canonical)

        for variant in variants:
            path = _branch_states(variant)
            states.update(path)

            for index, character in enumerate(variant):
                input_alphabet.add(character)
                step = (path[index], character, path[index + 1], None)
                if step not in seen:
                    seen.add(step)
                    transitions.append(step)

            # Lambda transition that emits the canonical form.
            step = (path[-1], LAMBDA, accepting, canonical)
            if step not in seen:
                seen.add(step)
                transitions.append(step)

    return {
        "name": "T_" + category,
        "category": category,
        "states": states,
        "input_alphabet": input_alphabet,
        "output_alphabet": output_alphabet,
        "transitions": transitions,
        "initial_state": START_STATE,
        "final_states": final_states,
    }


def build_transducer(category):
    """Build the pyformlang FST of one qualification category."""
    specification = transducer_specification(category)

    transducer = FST()
    for source, symbol, target, output in specification["transitions"]:
        if output is None:
            transducer.add_transition(source, symbol, target, [])
        else:
            transducer.add_transition(source, symbol, target, [output])

    transducer.add_start_state(specification["initial_state"])
    for state in specification["final_states"]:
        transducer.add_final_state(state)
    return transducer


def build_all_transducers():
    """Build one transducer per qualification category. Returns a dictionary category -> FST."""
    return {
        category: build_transducer(category)
        for category in profiles.category_names()
    }


def format_specification(category):
    """Return the 7-tuple of a transducer as readable text."""
    spec = transducer_specification(category)
    lines = []
    lines.append("Transducer " + spec["name"] +
                 "  M = (Q, Σ, Γ, δ, ω, q₀, F)")
    lines.append("  |Q|     = " + str(len(spec["states"])) + " states")
    lines.append("  Σ   = {" +
                 ", ".join(repr(symbol) for symbol in
                           sorted(spec["input_alphabet"])) + "}")
    lines.append("   Γ   = {" +
                 ", ".join(sorted(spec["output_alphabet"])) + "}")
    lines.append("  q₀      = " + spec["initial_state"])
    lines.append("  F       = {" +
                 ", ".join(sorted(spec["final_states"])) + "}")
    lines.append("  δ / ω : " + str(len(spec["transitions"])) +
                 " transitions, listed as (source, input, target, output)")
    for source, symbol, target, output in spec["transitions"]:
        shown_input = "λ" if symbol == LAMBDA else repr(symbol)
        shown_output = "λ" if output is None else output
        lines.append("    (" + source + ", " + shown_input + ", " +
                     target + ", " + shown_output + ")")
    return "\n".join(lines)



