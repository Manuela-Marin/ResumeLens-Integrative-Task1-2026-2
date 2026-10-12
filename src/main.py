import os
import sys

from . import classification
from . import dsl
from . import extraction
from . import ingestion
from . import normalization
from . import profiles
from . import visualization
from .visualization import diagram_exporter


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESUME_DIRECTORY = os.path.join(PROJECT_ROOT, "data", "resumes")
OUTPUT_DIRECTORY = os.path.join(PROJECT_ROOT, "output")

SEPARATOR = "-" * 70

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def _print_title(title):
    print()
    print(SEPARATOR)
    print(title)
    print(SEPARATOR)


def run_pipeline(text, show_stages=True):
    """Run the four stages over the text of a resume."""
    # Stage 1: extraction with regular expressions.
    extracted = extraction.extract(text)
    if show_stages:
        _print_title("Stage 1 - Extraction (regular expressions)")
        print("Name      :", extracted["name"])
        print("Email     :", extracted["email"])
        print("Phone     :", extracted["phone"])
        print("Location  :", extracted["location"])
        print("Role      :", extracted["role"])
        print("Education :", len(extracted["education"]), "record(s)")
        print("Experience:", len(extracted["experience"]), "entry(ies)")
        print("Raw skills:", ", ".join(extracted["raw_skills"]))

    # Stage 2: normalization with finite-state transducers.
    canonical, unknown = normalization.normalize(extracted["raw_skills"])
    if show_stages:
        _print_title("Stage 2 - Normalization (finite-state transducers)")
        print("Canonical :", ", ".join(canonical))
        if unknown:
            print("Not recognised by any transducer:", ", ".join(unknown))

    # Stage 3: pattern recognition with finite automata.
    results = classification.classify(canonical)
    if show_stages:
        _print_title("Stage 3 - Pattern recognition (finite automata)")
        for result in results:
            print(result["profile"], "(" + result["type"] + ")")
            print("   sequence:", ", ".join(result["sequence"]) or "(empty)")
            print("   verdict :", result["verdict"])
            if result["missing"]:
                print("   missing :", ", ".join(result["missing"]))

    # Stage 4: candidate profile language.
    sentence = dsl.build(extracted, canonical, results)
    valid, message = dsl.is_valid(sentence)
    if show_stages:
        _print_title("Stage 4 - Candidate profile language (textX)")
        print(sentence)
        print("Validation:", message)

    return {
        "extracted": extracted,
        "canonical": canonical,
        "unknown": unknown,
        "results": results,
        "sentence": sentence,
        "valid": valid,
        "message": message,
    }


def _write(text, path):
    """Write generated text to disk, always in UTF-8."""
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path


def _write_outputs(outcome, stem):
    """Validate the generated sentence and write every output file."""
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)

    dsl_path = _write(outcome["sentence"],
                      os.path.join(OUTPUT_DIRECTORY, stem + ".candidate"))

    if not outcome["valid"]:
        print()
        print("The generated profile is NOT valid, so no visualization was")
        print("produced.  Reason reported by textX:")
        print(outcome["message"])
        return [dsl_path]

    model = dsl.validate(outcome["sentence"])
    html_path = os.path.join(OUTPUT_DIRECTORY, stem + ".html")
    markdown_path = os.path.join(OUTPUT_DIRECTORY, stem + ".md")
    _write(visualization.render_html(model), html_path)
    _write(visualization.render_markdown(model), markdown_path)
    return [dsl_path, html_path, markdown_path]


def option_process_resume():
    """Menu option: run the full pipeline over one of the sample resumes."""
    names = ingestion.list_resumes(RESUME_DIRECTORY)
    if not names:
        print("No resumes found in", RESUME_DIRECTORY)
        return

    print()
    print("Available resumes:")
    for index, name in enumerate(names, start=1):
        print("  " + str(index) + ". " + name)
    answer = input("Choose a resume (number): ").strip()
    if not answer.isdigit() or not 1 <= int(answer) <= len(names):
        print("Invalid choice.")
        return

    name = names[int(answer) - 1]
    text = ingestion.load_resume(os.path.join(RESUME_DIRECTORY, name))

    outcome = run_pipeline(text)
    written = _write_outputs(outcome, os.path.splitext(name)[0])

    _print_title("Files written")
    for item in written:
        print(" ", item)
    accepted = classification.accepted_profiles(outcome["results"])
    print()
    print("Accepted profiles:", ", ".join(accepted) if accepted else "none")


def option_formal_definitions():
    """Menu option: show the formal definitions required by the assignment."""
    print()
    print("  1. Transducers  (7-tuple, stage 2)")
    print("  2. Automata     (5-tuple, stage 3)")
    answer = input("Choose (number): ").strip()

    if answer == "1":
        names = profiles.category_names()
        for index, name in enumerate(names, start=1):
            print("  " + str(index) + ". T_" + name)
        choice = input("Choose a transducer (number): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(names):
            _print_title("Formal definition")
            print(normalization.format_specification(names[int(choice) - 1]))
        else:
            print("Invalid choice.")
    elif answer == "2":
        names = profiles.profile_names()
        for index, name in enumerate(names, start=1):
            print("  " + str(index) + ". " + name)
        choice = input("Choose an automaton (number): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(names):
            _print_title("Formal definition")
            print(classification.format_specification(names[int(choice) - 1]))
        else:
            print("Invalid choice.")
    else:
        print("Invalid choice.")


def option_generate_diagrams():
    """Menu option: write the .dot diagrams and try to convert them to .png."""
    written = diagram_exporter.generate_all()
    _print_title("Diagrams written")
    for path in written:
        png = diagram_exporter.to_png(path)
        print(" ", path, "->",
              png if png else "(png skipped, pydot/Graphviz not available)")


def option_validate_profile():
    """Menu option: validate a candidate profile file written by hand."""
    path = input("Path of the .candidate file: ").strip()
    if not os.path.isfile(path):
        print("File not found:", path)
        return
    with open(path, "r", encoding="utf-8") as handle:
        text = handle.read()
    valid, message = dsl.is_valid(text)
    _print_title("Validation result")
    print("Valid:", valid)
    print(message)


MENU = """
======================================================================
ResumeLens - Formal Language-Based Resume Screening
======================================================================
  1. Process a resume (runs the four stages)
  2. Show a formal definition (7-tuple / 5-tuple)
  3. Export the diagrams of the transducers and the automata
  4. Validate a candidate profile file
  0. Exit
"""


def main():
    """Run the console interface."""
    while True:
        print(MENU)
        option = input("Option: ").strip()
        if option == "1":
            option_process_resume()
        elif option == "2":
            option_formal_definitions()
        elif option == "3":
            option_generate_diagrams()
        elif option == "4":
            option_validate_profile()
        elif option == "0":
            print("Goodbye.")
            return
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()