import os

from .. import profiles
from ..classification import LAMBDA as CLASSIFICATION_LAMBDA
from ..classification import automaton_specification
from ..normalization import LAMBDA as NORMALIZATION_LAMBDA
from ..normalization import transducer_specification

PROJECT_ROOT = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

OUTPUT_DIRECTORY = os.path.join(PROJECT_ROOT, "docs", "diagrams")


def _node_name(state):
    """Return a DOT-safe node identifier for a state name."""
    safe = []
    for character in str(state):
        if character.isalnum() or character == "_":
            safe.append(character)
        else:
            safe.append("_" + str(ord(character)) + "_")
    return "n_" + "".join(safe)


def _escape_label(text):
    """Escape the characters that are special inside a DOT label."""
    return str(text).replace("\\", "\\\\").replace('"', '\\"')


def _short_label(state):
    """Return a compact label for a prefix-tree state."""
    if state.startswith("q_"):
        return state[-1]
    return state


def transducer_dot(category):
    """Return the DOT source of the transducer of one category."""
    spec = transducer_specification(category)

    lines = ["digraph " + spec["name"] + " {",
             '    node [shape=circle, fontsize=9, width=0.25, height=0.25,'
             ' fixedsize=false];',
             '    edge [fontsize=9];',
             '    __start [shape=point, label=""];']

    for state in sorted(spec["states"]):
        shape = "doublecircle" if state in spec["final_states"] else "circle"
        lines.append("    " + _node_name(state) + ' [shape=' + shape +
                     ', label="' + _escape_label(_short_label(state)) + '"];')

    lines.append("    __start -> " + _node_name(spec["initial_state"]) + ";")

    for source, symbol, target, output in spec["transitions"]:
        shown_input = "lambda" if symbol == NORMALIZATION_LAMBDA else symbol
        shown_output = "lambda" if output is None else output
        label = _escape_label(shown_input) + ":" + _escape_label(shown_output)
        lines.append("    " + _node_name(source) + " -> " +
                     _node_name(target) + ' [label="' + label + '"];')

    lines.append("}")
    return "\n".join(lines) + "\n"


def automaton_dot(profile_name):
    """Return the DOT source of the transition diagram of one automaton."""
    spec = automaton_specification(profile_name)

    lines = ["digraph " + profile_name + " {", "    rankdir=LR;",
             '    node [shape=circle, fontsize=10];',
             '    __start [shape=point, label=""];']

    for state in spec["states"]:
        shape = "doublecircle" if state in spec["final_states"] else "circle"
        lines.append("    " + _node_name(state) + " [shape=" + shape +
                     ', label="' + _escape_label(state) + '"];')

    lines.append("    __start -> " + _node_name(spec["initial_state"]) + ";")

    grouped = {}
    order = []
    for source, symbol, target in spec["transitions"]:
        key = (source, target)
        if key not in grouped:
            grouped[key] = []
            order.append(key)
        shown = "lambda" if symbol == CLASSIFICATION_LAMBDA else symbol
        grouped[key].append(shown)

    for source, target in order:
        label = ", ".join(grouped[(source, target)])
        lines.append("    " + _node_name(source) + " -> " +
                     _node_name(target) +
                     ' [label="' + _escape_label(label) + '"];')

    lines.append("}")
    return "\n".join(lines) + "\n"


def generate_all(directory=None):
    """Write every .dot file and return the list of paths written."""
    if directory is None:
        directory = OUTPUT_DIRECTORY
    os.makedirs(directory, exist_ok=True)

    written = []
    for category in profiles.category_names():
        path = os.path.join(directory, "fst_" + category + ".dot")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(transducer_dot(category))
        written.append(path)

    for profile_name in profiles.profile_names():
        path = os.path.join(directory, "fa_" + profile_name + ".dot")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(automaton_dot(profile_name))
        written.append(path)

    return written


def to_png(dot_path):
    """Convert one .dot file to .png with pydot"""
    try:
        import pydot
    except ImportError:
        return None
    try:
        (graph,) = pydot.graph_from_dot_file(dot_path)
        png_path = dot_path[:-4] + ".png"
        graph.write_png(png_path)
        return png_path
    except Exception:
        return None