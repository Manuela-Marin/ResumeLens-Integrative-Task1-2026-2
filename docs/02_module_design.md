# Module design

This section corresponds to deliverable 2a of the assignment. Here, I explain how I organized the project into modules, what each module does, and what its functions receive and return.

---

## 1. Domain analysis

### Main concepts


| Concept                 | Description                                                                                                                                    |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Résumé                | The text file containing the information written by a candidate. It is the input of the system.                                                |
| Raw skill               | A skill as it appears in the résumé, such as`React.js`.                                                                                      |
| Canonical qualification | The standard name I use to represent equivalent skills. For example,`React.js` becomes `REACT`.                                                |
| Category                | A group of related qualifications, such as`FRONTEND`. Each category has its own transducer.                                                    |
| Stage                   | One step in the pattern of a profile. A stage can accept different alternative qualifications and can be required or optional.                 |
| Profile                 | An ordered sequence of stages that represents a type of candidate, such as`FULL_STACK_DEVELOPER`.                                              |
| Verdict                 | The result returned by an automaton:`ACCEPTED` or `REJECTED`.                                                                                  |
| Candidate profile       | The final representation of a candidate in the DSL. It contains the information extracted from the résumé and the results of the evaluation. |

### Relationships and constraints

While analyzing the problem, I identified the following relationships and constraints:

- Each raw skill can be mapped to at most one canonical qualification. If none of the transducers recognizes a skill, I report it as unrecognized instead of assigning a qualification without evidence.
- Each canonical qualification belongs to exactly one category.
- Each profile has an ordered sequence of stages. The order matters because it determines how the qualifications must be recognized.
- A candidate can be accepted by none, one, or several profiles. I do not assume that every candidate must match a profile.
- The four profiles must use the same general solution instead of having four separate implementations.

### Profiles included in the project


| Profile                     | Origin                                                             |
| --------------------------- | ------------------------------------------------------------------ |
| `FULL_STACK_DEVELOPER`      | The first reference profile in the assignment.                     |
| `MACHINE_LEARNING_ENGINEER` | The second reference profile in the assignment.                    |
| `MOBILE_DEVELOPER`          | An additional profile I defined for the software engineering area. |
| `DATA_ENGINEER`             | An additional profile I defined for the AI and data area.          |

---

## 2. Architecture

I organized the project as a pipeline where the output of one stage becomes the input of the next one.

```text
                      resume file
                           |
                           v
                   +----------------+
                   |   ingestion    |   reads the text
                   +----------------+
                           | resume text
                           v
                   +----------------+
                   |   extraction   |   stage 1: regular expressions
                   +----------------+
                           | extracted information
                           v
                   +----------------+
                   | normalization  |   stage 2: transducers
                   +----------------+
                           | canonical qualifications
                           v
                   +----------------+
                   | classification |   stage 3: automata
                   +----------------+
                           | result for each profile
                           v
                   +----------------+
                   |      dsl       |   stage 4: grammar
                   +----------------+
                           | validated model
                           v
                   +----------------+
                   | visualization  |   HTML / Markdown / DOT
                   +----------------+

   profiles   <--- used by normalization, classification and visualization
   main       <--- coordinates the complete process
```

I separated the stages so that each one has a specific responsibility. `ingestion` reads the résumé, `extraction` identifies the information, `normalization` standardizes the skills, `classification` evaluates the profiles, `dsl` builds and validates the candidate representation, and `visualization` generates the corresponding outputs.

The `main` module connects all these parts and provides the menu through which the user can run the program.

I also tried to keep the dependencies organized. The modules that implement each stage do not need to import the next stage in the pipeline. Instead, `main` coordinates the process and passes the results between modules. This makes it easier to test each stage separately.

### Package layout

```text
src/
├── __init__.py
├── main.py                      console interface
├── profiles/
│   ├── __init__.py              exposes both modules
│   ├── qualifications.py        QUALIFICATION_VARIANTS
│   └── patterns.py              PROFILE_PATTERNS
├── ingestion/
│   ├── __init__.py
│   └── resume_loader.py
├── extraction/
│   ├── __init__.py
│   ├── patterns.py              compiled regular expressions
│   └── extractor.py             extraction functions
├── normalization/
│   ├── __init__.py
│   ├── transducers.py           FST construction and 7-tuple
│   └── normalizer.py            normalization and ordering
├── classification/
│   ├── __init__.py
│   ├── automata.py              automaton construction and 5-tuple
│   └── classifier.py            profile evaluation
├── dsl/
│   ├── __init__.py
│   ├── candidate.tx             textX grammar
│   ├── builder.py               structured data -> sentence
│   └── validator.py             sentence validation
└── visualization/
    ├── __init__.py
    ├── html_renderer.py
    ├── markdown_renderer.py
    └── diagram_exporter.py      DOT export for transducers and automata
```

In `normalization` and `classification`, I separated the construction of the formal models from their execution. For example, `transducers.py` defines how the transducers are built and how their 7-tuple is represented, while `normalizer.py` uses them to normalize the skills. I followed the same idea with `automata.py` and `classifier.py`.

I made this separation because the assignment requires the formal definitions, and keeping them in specific modules makes them easier to find and understand.

### How I implemented the general solution

One of the main design decisions was to keep the profile information separate from the algorithms.

The `profiles` package stores the qualification variants and the stages of each profile. The other packages contain the operations that work with this information, such as building transducers, building automata, normalizing qualifications, and evaluating candidates.

This means I do not need to write a different algorithm for every profile. The same functions work with the profile definitions stored in `profiles`. If I need to add another profile, I can define its stages there and reuse the existing algorithms, provided the new profile follows the same structure.

---

## 3. Packages

### 3.1 `src.profiles`

I created this package to store the information used by the transducers and automata. It contains the qualification variants and the stages that make up each profile.


| Name                     | Module              | Content                                                                                                |
| ------------------------ | ------------------- | ------------------------------------------------------------------------------------------------------ |
| `QUALIFICATION_VARIANTS` | `qualifications.py` | Maps each category to its canonical qualifications and their variants.                                 |
| `PROFILE_PATTERNS`       | `patterns.py`       | Stores each profile and its ordered stages, including alternatives and whether each stage is required. |

The package also provides the following functions:


| Function                     | Input          | Output                                       |
| ---------------------------- | -------------- | -------------------------------------------- |
| `category_names()`           | None           | Names of the 12 qualification categories.    |
| `canonical_qualifications()` | None           | All canonical qualifications.                |
| `category_of(canonical)`     | A string       | The category of the qualification, or`None`. |
| `profile_names()`            | None           | Names of the four profiles.                  |
| `stages_of(profile)`         | A profile name | The ordered list of stages for that profile. |

### 3.2 `src.ingestion`

This package handles reading the résumé files. I kept it separate from extraction because reading the text and identifying information in that text are two different tasks.


| Function                  | Input          | Output                                                                         |
| ------------------------- | -------------- | ------------------------------------------------------------------------------ |
| `load_resume(path)`       | File path      | The résumé text. Raises`FileNotFoundError` if the file does not exist.       |
| `list_resumes(directory)` | Directory path | Sorted names of the`.txt` files, or an empty list if the directory is missing. |

This way, `ingestion` is responsible for obtaining the text, while `extraction` is responsible for recognizing the information inside it.

### 3.3 `src.extraction` — Stage 1

In this stage, I use regular expressions to identify the information contained in the résumé.

The `patterns.py` module contains twelve compiled regular expressions. Each one is designed to recognize a specific type of information:

`NAME_PATTERN`, `EMAIL_PATTERN`, `PHONE_PATTERN`, `LOCATION_PATTERN`, `ROLE_PATTERN`, `SUMMARY_PATTERN`, `EDUCATION_PATTERN`, `EXPERIENCE_PATTERN`, `RESPONSIBILITY_PATTERN`, `TOTAL_EXPERIENCE_PATTERN`, `SKILLS_BLOCK_PATTERN`, and `SKILL_ITEM_PATTERN`.

The `extractor.py` module applies these patterns through the following functions:


| Function                         | Input         | Output                                                                                                       |
| -------------------------------- | ------------- | ------------------------------------------------------------------------------------------------------------ |
| `extract_contact(text)`          | Résumé text | A dictionary with`name`, `email`, `phone`, `location`, and `role`. Values are `None` when no match is found. |
| `extract_summary(text)`          | Résumé text | The summary as a single line, or`None`.                                                                      |
| `extract_education(text)`        | Résumé text | A list of dictionaries containing`degree`, `field`, `institution`, and `year`.                               |
| `extract_experience(text)`       | Résumé text | A list of dictionaries containing`title`, `organization`, `years`, and `responsibilities`.                   |
| `extract_total_experience(text)` | Résumé text | The total experience as an integer, or`None`.                                                                |
| `extract_skills(text)`           | Résumé text | A list of raw skill strings, preserving how they were written.                                               |
| `extract(text)`                  | Résumé text | A dictionary containing all the extracted information.                                                       |

The `extract()` function brings the results together in a single dictionary. 

### 3.4 `src.normalization` — Stage 2

In this stage, I use finite-state transducers to convert different ways of writing a skill into its canonical qualification.

I divided the work between `transducers.py` and `normalizer.py`.

**`transducers.py`**


| Function                             | Input         | Output                                                                |
| ------------------------------------ | ------------- | --------------------------------------------------------------------- |
| `transducer_specification(category)` | Category name | A dictionary containing the seven components of the transducer tuple. |
| `build_transducer(category)`         | Category name | A`pyformlang.fst.FST` object.                                         |
| `build_all_transducers()`            | None          | A dictionary mapping categories to their transducers.                 |
| `format_specification(category)`     | Category name | The 7-tuple in readable text.                                         |

**`normalizer.py`**


| Function                              | Input                                       | Output                                                                                          |
| ------------------------------------- | ------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `normalize_one(raw, transducers)`     | One raw skill                               | Its canonical form, or`None` if it is not recognized.                                           |
| `normalize(raw_skills, transducers)`  | A list of raw skills                        | A pair containing the canonical qualifications and the unknown skills.                          |
| `canonical_order(canonical, profile)` | A list of qualifications and a profile name | The qualifications ordered according to the profile's stages, with one qualification per stage. |

I kept the transducer construction separate from normalization so that I can inspect the formal definition independently of the process that uses it.

### 3.5 `src.classification` — Stage 3

In this stage, I use finite automata to check whether the normalized qualifications follow the pattern of each profile.

I also divided this package into two modules.

**`automata.py`**


| Function                           | Input        | Output                                                              |
| ---------------------------------- | ------------ | ------------------------------------------------------------------- |
| `automaton_specification(profile)` | Profile name | A dictionary containing the five components of the automaton tuple. |
| `automaton_type(profile)`          | Profile name | `"NFA-lambda"` or `"NFA"`.                                          |
| `build_automaton(profile)`         | Profile name | A`pyformlang.finite_automaton.EpsilonNFA` object.                   |
| `build_all_automata()`             | None         | A dictionary mapping profiles to their automata.                    |
| `format_specification(profile)`    | Profile name | The 5-tuple in readable text.                                       |

**`classifier.py`**


| Function                               | Input                                              | Output                                                                              |
| -------------------------------------- | -------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `accepts(profile, sequence, automata)` | Profile name, qualification sequence, and automata | A Boolean indicating whether the sequence is accepted.                              |
| `missing_stages(profile, canonical)`   | Profile name and qualifications                    | Names of the required stages that are not satisfied.                                |
| `classify(canonical, automata)`        | Canonical qualifications                           | A list of dictionaries with`profile`, `type`, `sequence`, `verdict`, and `missing`. |
| `accepted_profiles(results)`           | Classification results                             | Names of the profiles that accepted the candidate.                                  |

With this separation, I can define the automata independently and then use them to evaluate the candidate against all four profiles.

### 3.6 `src.dsl` — Stage 4

I created this package to build the candidate profile using the DSL and verify that it follows the grammar.

The `candidate.tx` file contains the textX grammar, and its EBNF description is included in `03_formalization.md`.


| Function                               | Module         | Input                      | Output                                                        |
| -------------------------------------- | -------------- | -------------------------- | ------------------------------------------------------------- |
| `build(extracted, canonical, results)` | `builder.py`   | Results from stages 1–3   | A string representing a sentence of the language.             |
| `meta_model()`                         | `validator.py` | None                       | The textX meta-model, built once.                             |
| `validate(text)`                       | `validator.py` | A sentence of the language | The textX model, or a`TextXError` if the sentence is invalid. |
| `validate_file(path)`                  | `validator.py` | File path                  | The textX model built from the file.                          |
| `is_valid(text)`                       | `validator.py` | A sentence of the language | A pair containing a Boolean and a message.                    |

The builder takes the results of the previous stages and creates the candidate representation. The validator then checks whether that representation follows the grammar. This lets me detect invalid candidate profiles instead of assuming that every generated or manually written file is correct.

### 3.7 `src.visualization`

I use this package to generate different representations of the validated candidate and the formal models.


| Function                   | Module                 | Input              | Output                                                           |
| -------------------------- | ---------------------- | ------------------ | ---------------------------------------------------------------- |
| `render_html(model)`       | `html_renderer.py`     | A textX model      | HTML following the layout of`OutputExample.html`.                |
| `render_markdown(model)`   | `markdown_renderer.py` | A textX model      | A Markdown representation.                                       |
| `write(text, path)`        | `markdown_renderer.py` | Text and file path | The path of the written file.                                    |
| `transducer_dot(category)` | `diagram_exporter.py`  | Category name      | DOT source with edges labelled`input:output`.                    |
| `automaton_dot(profile)`   | `diagram_exporter.py`  | Profile name       | DOT source for the automaton's transition diagram.               |
| `generate_all(directory)`  | `diagram_exporter.py`  | Directory path     | A list of the generated`.dot` files.                             |
| `to_png(dot_path)`         | `diagram_exporter.py`  | DOT file path      | The PNG file path, or`None` if pydot or Graphviz is unavailable. |

The renderers receive the validated textX model instead of the original extraction dictionary.

### 3.8 `src.main`

The `main.py` module is the entry point of the program. It provides the console menu and coordinates the different stages.

The `run_pipeline(text)` function runs the four stages and returns the intermediate results. The menu options use this process to generate the output files, display formal definitions, export diagrams, and validate candidate files.


| Menu option | What it does                                                                                                |
| ----------- | ----------------------------------------------------------------------------------------------------------- |
| 1           | Processes a résumé from`data/resumes/` and generates `.candidate`, `.html`, and `.md` files in `output/`. |
| 2           | Displays the 7-tuple of a transducer or the 5-tuple of an automaton.                                        |
| 3           | Exports the diagrams to`docs/diagrams/`.                                                                    |
| 4           | Validates a candidate profile file written manually or generated previously.                                |

---

## 4. Diagrams required by the assignment

The assignment asks for two types of diagrams, so I organized their generation separately.


| Requirement                                 | Page | How many                        | Produced with                          |
| ------------------------------------------- | ---- | ------------------------------- | -------------------------------------- |
| Graphical representation of the transducers | 4    | one per transducer, 12 in total | `diagram_exporter`, using DOT and PNG. |
| Transition diagram for each automaton       | 5    | one per automaton, 4 in total   | diagram_exporter, using DOT and PNG.   |

The automata have seven states each, while the transducers are character-level prefix trees that can contain from around ten to more than a hundred states. I generate all the diagrams automatically from the implementation using `diagram_exporter`. This avoids drawing them manually and helps ensure that the diagrams represent the formal models defined in the code. I export the diagrams in DOT format and convert them to PNG using `pydot` and Graphviz.

---

## 5. Techniques not covered in class

While developing the project, I identified four requirements that are not directly covered in the course material. For each one, I used a simple solution without adding unnecessary dependencies.


| Requirement                                                  | Why it is an exception                 | Solution adopted                                                             |
| ------------------------------------------------------------ | -------------------------------------- | ---------------------------------------------------------------------------- |
| Keep the extracted information in a file or data structure  | No lecture uses file input/output      | A plain Python`dict`; `open` from the standard library in `ingestion`        |
| Reject invalid representations                               | textX is taught without error handling | Let`TextXError` propagate from `validate` and catch it in `is_valid`         |
| Generate HTML or Markdown                                    | Not covered                            | String composition, no template library                                      |
| Implement the UI and the tests                               | Not covered                            | A console menu with`input`/`print`, and `unittest` from the standard library |

For these cases, I tried to keep the implementation as simple as possible and use Python's standard tools whenever they were enough to meet the assignment requirements.
