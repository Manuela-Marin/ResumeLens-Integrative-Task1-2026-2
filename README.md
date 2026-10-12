# ResumeLens-Integrative-Task1-2026-2

Integrative Task 1 — Computación y Estructuras Discretas III — 2026-2


|                 |                                          |
| --------------- | ---------------------------------------- |
| **Student**     | Manuela Marín Millán                   |
| **Course code** | 09772                                    |
| **Group**       | 3 (professor Andrés A. Aristizábal P.) |
| **IDE used**    | IntelliJ IDEA                            |
| **Language**    | Python 3                                 |

## Problem

Recruitment requires checking whether the qualifications declared in a
résumé satisfy those expected for a professional profile. The same
qualification is written in many ways — `JavaScript`, `Javascript`, `JS` all
denote the same language — and different profiles require different
combinations.

ResumeLens decides whether the qualifications explicitly identified in a
résumé satisfy a formally defined qualification pattern. It does **not**
rank candidates and does **not** make hiring decisions.

## Approach

The program is a pipeline of four stages, each one built on a different
formal language model:


| Stage                                | Model                    | Library      |
| ------------------------------------ | ------------------------ | ------------ |
| 1. Résumé information extraction   | Regular expressions      | `re`         |
| 2. Qualification normalization       | Finite-state transducers | `pyformlang` |
| 3. Qualification pattern recognition | Finite automata          | `pyformlang` |
| 4. Candidate profile language        | Context-free grammar     | `textX`      |

The system supports four professional profiles: `FULL_STACK_DEVELOPER` and
`MACHINE_LEARNING_ENGINEER`, the two reference profiles of the assignment,
plus `MOBILE_DEVELOPER` and `DATA_ENGINEER`, the two additional profiles
defined by this project in the areas of software engineering and AI/data.
All four are processed by the same general engine.

---

## Installation

Python 3.8 or later is required.

```bash
pip install -r requirements.txt
```

pydot and a Graphviz installation are only needed to convert the diagrams of the transducers and the automata to PNG. Without them the program still writes the .dot files, which can be pasted into https://dreampuf.github.io/GraphvizOnline/.

### Opening the project in IntelliJ IDEA

1. `File > Open` and select the `ResumeLens` folder.
2. `File > Project Structure > SDK`: choose a Python 3 interpreter.

`src` is a package, so the repository root is the import root and nothing
else has to be configured. From a terminal, run everything from the
repository root:

```bash
python -m src.main
```

---

## Repository layout

```
ResumeLens/
├── README.md
├── requirements.txt
├── docs/                      design documents, in Markdown
│   └── diagrams/              transducer and automaton diagrams
├── src/
│   ├── main.py                console interface
│   ├── profiles/              the four profiles, as data
│   ├── ingestion/             reading a résumé from disk
│   ├── extraction/            stage 1, regular expressions
│   ├── normalization/         stage 2, finite-state transducers
│   ├── classification/        stage 3, finite automata
│   ├── dsl/                   stage 4, candidate profile language
│   └── visualization/         HTML, Markdown and diagram output
├── data/resumes/              sample résumés
└── tests/                     unit tests
```

The design of each package, with the inputs and outputs of every function,
is in [`docs/02_module_design.md`](docs/02_module_design.md).

---

## Tests

```bash
python -m unittest discover -s tests -t .
```

68 tests, one file per stage. The scenarios they cover are specified in
[`docs/04_test_cases.md`](docs/04_test_cases.md).

## State of the project


| Stage                               | State |
| ----------------------------------- | ----- |
| Project setup                       | done  |
| Literature review                   | done  |
| Module and test design              | done  |
| 1. Extraction                       | done  |
| 2. Normalization                    | done  |
| 3. Classification                   | done  |
| 4. Candidate profile language       | done  |
| Visualization and console interface | done  |
| Unit tests                          | done  |

```

```
