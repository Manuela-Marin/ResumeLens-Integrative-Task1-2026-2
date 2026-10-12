# Formalization

Deliverable 2b of the assignment. This document gives the formal definition
of every model used by ResumeLens: the regular expressions of stage 1, the
7-tuple of each transducer of stage 2, the 5-tuple of each automaton of
stage 3, and the EBNF description of the language of stage 4.

Every figure in this document was obtained by running the implementation.
Menu option 2 of the console interface prints the full tuple of any
transducer or automaton.

---

## 1. Stage 1 — Regular expressions

In this stage, I use regular expressions to recognize the different types of information in a résumé. I implemented the patterns in `src/extraction/patterns.py`. using Python's `re` module.

The following table shows each pattern, the information it recognizes, and how it works.


| Information            | Pattern                                            | Language recognised                                                                                                                                                         |
| ---------------------- | -------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name                   | `^([A-Z][A-Za-z'\-]+( [A-Z][A-Za-z'\-]+)+)[ ]*$`   | A complete line containing two or more capitalized words. Each word starts with an uppercase letter and continues with letters, apostrophes, or hyphens.                    |
| E-mail                 | `[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}` | A local part containing letters, digits, and ._%+-, followed by @, a domain, a dot, and a top-level domain with at least two letters                                        |
| Telephone              | `(\+\d{1,3}[ \-]?)?\d{3}[ \-]?\d{3}[ \-]?\d{3,4}`  | An optional international prefix followed by groups of digits separated by spaces, hyphens, or nothing. It accepts formats such as 555-555-555, 555 555 555, and 555555555. |
| Location               | `^Location:[ ]*(.+)$`                              | The label Location:, followed by optional spaces and the rest of the line.                                                                                                  |
| Current role           | `^Role:[ ]*(.+)$`                                  | The label Role:, followed by optional spaces and the rest of the line.                                                                                                      |
| Summary                | `^Summary:[ ]*\n(.+?)(\n[ ]*\n\Z)`                 | The label Summary: followed by the text, including newlines, until the first blank line or the end of the input.                                                            |
| Academic qualification |                                                    | A degree keyword, the word in, a field of study, an institution, and a four-digit year, separated by commas where required.                                                 |
| Experience entry       |                                                    | A job title, an organization, and a number of years, separated by vertical bars.                                                                                            |
| Responsibility         | `^-[ ]+(.+?)[ ]*$`                                 | A line that starts with a hyphen and a space.                                                                                                                               |
| Total experience       | `(\d+)[ ]+years?[ ]+of[ ]+experience`              | A number followed by the phrase years of experience.                                                                                                                        |
| Skills block           | `^Technical Skills:[ ]*\n(.+?)(\n[ ]*\n\Z)`        | The label Technical Skills: followed by the text until the first blank line or the end of the input.                                                                        |
| Skill item             | `[^,;\n]+`                                         | A sequence of characters that does not contain a comma, semicolon, or newline. I use it to split the skills block into individual items.                                    |

These expressions use character classes and ranges, predefined classes such as \d and \w, alternation, quantifiers such as ?, +, *, and {n,m}, lazy matching with +?, and boundary matchers such as ^, $, and \Z. These features allow me to define exactly what kind of text each pattern should recognize.

Scope of this stage. At this point, I only recognize text. I do not determine whether JS and Javascript represent the same qualification, and I do not classify the candidate's profile. Those tasks belong to later stages.

---

## 2. Stage 2 — Finite-state transducers

### 2.1 Why I chose character-level transducers

I decided to make the transducers read one character per transition. This follows the approach used in several finite-state transducer examples, including the transducer for the verb llorar, where each transition processes one character and produces an output when needed.

I chose this approach mainly because some qualifications contain spaces, such as scikit learn, Tensor Flow, and Py Torch. With a character-level transducer, the space is simply another symbol in the input alphabet, so I can process the entire expression without splitting it into separate tokens.

### 2.2 How I built the transducers

I implemented one transducer for each qualification category. Each transducer uses a prefix tree:

As the transducer reads the characters of a variant, it moves through the corresponding branch without producing output.

Once it has read the complete variant, a λ transition produces the canonical form and moves to the accepting state associated with that form.

I chose to produce the output through the λ transition instead of attaching it to the last character. This is important when one qualification is a prefix of another. For example, Java and JavaScript must produce JAVA and JAVASCRIPT, respectively.

The same situation occurs with Swift and SwiftUI, React and React Native, and Room and Room Database. By waiting until the complete variant has been recognized, I avoid mixing their canonical forms..

### 2.3 Formal definition

Every transducer is a **non-deterministic finite-state transducer** defined as

> M = (Q, Σ, Γ, δ, ω, q₀, F)
>
> where
>
> Q: is the set of states.
>
> Σ : is the input alphabet.
>
> Γ : is the output alphabet.
>
> δ: is the transition relation.
>
> ω: is the output function.
>
> q₀: is the initial state.
>
> F: is the set of accepting states.

In my implementation, the transition relation can include λ transitions because I use them to produce the canonical output after recognizing a complete variant. The transition relation is also partial, since each state only has transitions for the characters that continue one of its branches.

### 2.4 The twelve transducers

I implemented twelve transducers, one for each qualification category. Their sizes depend on the number and length of the variants they recognize.


| Transducer           | Canonical forms | \|Q\| | \|Σ\| | Transitions |
| -------------------- | --------------- | ----- | ------ | ----------- |
| `T_LANGUAGE`         | 8               | 98    | 26     | 108         |
| `T_FRONTEND`         | 3               | 31    | 17     | 35          |
| `T_BACKEND`          | 3               | 40    | 19     | 44          |
| `T_DATABASE`         | 4               | 65    | 21     | 71          |
| `T_DATA_LIBRARY`     | 2               | 27    | 10     | 29          |
| `T_ML_FRAMEWORK`     | 4               | 141   | 27     | 147         |
| `T_API`              | 2               | 37    | 21     | 40          |
| `T_MOBILE_FRAMEWORK` | 4               | 61    | 24     | 65          |
| `T_MOBILE_STORAGE`   | 3               | 46    | 20     | 49          |
| `T_DATA_PLATFORM`    | 3               | 50    | 17     | 53          |
| `T_ORCHESTRATION`    | 2               | 50    | 20     | 53          |
| `T_VERSION_CONTROL`  | 1               | 10    | 6      | 11          |

The complete 7-tuple of any of them is printed by option 2 of the console
interface, and its diagram is in `docs/diagrams/fst_<category>.dot|.png`.

Because the states of a prefix tree are exactly its prefixes, the seven
components are fully determined by the table of variants in
`src/profiles/qualifications.py`:

* **Q** = {q₀} ∪ { q_p : p is a non-empty prefix of some variant } ∪
  { F_c : c is a canonical form of the category }
* **Σ** = the set of characters occurring in the variants
* **Γ** = the set of canonical forms of the category
* **δ, ω** = for every variant `u = a₁…aₙ` of the canonical form `c`:
  δ(q_{a₁…a_{k-1}}, a_k) = q_{a₁…a_k} with ω = λ, for k = 1…n;
  and δ(q_u, λ) = F_c with ω = c
* **q₀** = q₀
* **F** = { F_c : c is a canonical form of the category }

#### Worked example: `T_VERSION_CONTROL`

M = (Q, Σ, Γ, δ, ω, q₀, F) with

* Q = {q₀, q_G, q_Gi, q_Git, q_g, q_gi, q_git, q_GI, q_GIT, F_GIT}
* Σ = {`G`, `I`, `T`, `g`, `i`, `t`}
* Γ = {`GIT`}
* q₀ = q₀
* F = {F_GIT}


| δ / ω | source | input | target | output |
| ------- | ------ | ----- | ------ | ------ |
| 1       | q₀    | `G`   | q_G    | λ     |
| 2       | q_G    | `i`   | q_Gi   | λ     |
| 3       | q_Gi   | `t`   | q_Git  | λ     |
| 4       | q_Git  | λ    | F_GIT  | `GIT`  |
| 5       | q₀    | `g`   | q_g    | λ     |
| 6       | q_g    | `i`   | q_gi   | λ     |
| 7       | q_gi   | `t`   | q_git  | λ     |
| 8       | q_git  | λ    | F_GIT  | `GIT`  |
| 9       | q_G    | `I`   | q_GI   | λ     |
| 10      | q_GI   | `T`   | q_GIT  | λ     |
| 11      | q_GIT  | λ    | F_GIT  | `GIT`  |

It accepts the three variants `Git`, `git` and `GIT` and translates all
three into `GIT`. The branches for `Git` and for `GIT` share the state q_G,
which is the prefix tree at work.

### 2.5 Qualification variants

I defined the following variants for the project. The goal is to recognize different ways of writing a qualification and convert them into a consistent canonical form.


| Category         | Canonical form         | Variants                                                               |
| ---------------- | ---------------------- | ---------------------------------------------------------------------- |
| LANGUAGE         | `JAVASCRIPT`           | JS, Javascript, JavaScript                                             |
| LANGUAGE         | `TYPESCRIPT`           | TS, Typescript, TypeScript                                             |
| LANGUAGE         | `PYTHON`               | Python, python, Python3                                                |
| LANGUAGE         | `JAVA`                 | Java, java                                                             |
| LANGUAGE         | `KOTLIN`               | Kotlin, kotlin                                                         |
| LANGUAGE         | `SWIFT`                | Swift, swift                                                           |
| LANGUAGE         | `DART`                 | Dart, dart                                                             |
| LANGUAGE         | `SCALA`                | Scala, scala                                                           |
| FRONTEND         | `REACT`                | React, React.js, ReactJS                                               |
| FRONTEND         | `ANGULAR`              | Angular, AngularJS                                                     |
| FRONTEND         | `VUE`                  | Vue, Vue.js, VueJS                                                     |
| BACKEND          | `NODE_JS`              | NodeJS, Node.js, Node                                                  |
| BACKEND          | `DJANGO`               | Django, django                                                         |
| BACKEND          | `SPRING_BOOT`          | Spring Boot, SpringBoot, Spring                                        |
| DATABASE         | `POSTGRESQL`           | Postgres, PostgreSQL, postgres                                         |
| DATABASE         | `NOSQL`                | NoSQL, NOSQL, No SQL                                                   |
| DATABASE         | `BIGQUERY`             | BigQuery, Big Query, bigquery                                          |
| DATABASE         | `SQL`                  | SQL, sql                                                               |
| DATA_LIBRARY     | `PANDAS`               | pandas, Pandas                                                         |
| DATA_LIBRARY     | `NUMPY`                | numpy, NumPy, Numpy                                                    |
| ML_FRAMEWORK     | `SCIKIT_LEARN`         | sklearn, scikit learn, Scikit-learn                                    |
| ML_FRAMEWORK     | `TENSORFLOW`           | TensorFlow, Tensor Flow, tensorflow                                    |
| ML_FRAMEWORK     | `PYTORCH`              | PyTorch, Py Torch, pytorch                                             |
| ML_FRAMEWORK     | `ML_MODEL_DEVELOPMENT` | Machine-learning model development, Machine learning model development |
| API              | `REST_API`             | REST APIs, REST API, RESTful APIs                                      |
| API              | `GRAPHQL`              | GraphQL, graphql, Graph QL                                             |
| MOBILE_FRAMEWORK | `ANDROID_SDK`          | Android SDK, Android, AndroidSDK                                       |
| MOBILE_FRAMEWORK | `FLUTTER`              | Flutter, flutter                                                       |
| MOBILE_FRAMEWORK | `REACT_NATIVE`         | React Native, ReactNative                                              |
| MOBILE_FRAMEWORK | `SWIFTUI`              | SwiftUI, Swift UI                                                      |
| MOBILE_STORAGE   | `SQLITE`               | SQLite, sqlite, SQLite3                                                |
| MOBILE_STORAGE   | `FIREBASE`             | Firebase, firebase                                                     |
| MOBILE_STORAGE   | `ROOM`                 | Room, Room Database                                                    |
| DATA_PLATFORM    | `SPARK`                | Spark, Apache Spark, PySpark                                           |
| DATA_PLATFORM    | `HADOOP`               | Hadoop, Apache Hadoop                                                  |
| DATA_PLATFORM    | `KAFKA`                | Kafka, Apache Kafka                                                    |
| ORCHESTRATION    | `AIRFLOW`              | Airflow, Apache Airflow, airflow                                       |
| ORCHESTRATION    | `DBT`                  | dbt, DBT, Data Build Tool                                              |
| VERSION_CONTROL  | `GIT`                  | Git, git, GIT                                                          |

### 2.6 Canonical ordering

After normalizing the qualifications, I also need to put them in a consistent order based on the selected profile. Otherwise, the output could change depending on the order in which the candidate listed their skills.

I implemented this rule in normalizer.canonical_order. The program goes through the stages of the selected profile in order and includes the first alternative in each stage that the candidate actually has. If the candidate does not have a qualification that satisfies a stage, that stage does not add anything to the result.

For example, when I use the Full Stack Developer profile with the corresponding résumé, the resulting sequence is:

```
JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT
```

The sequence remains the same regardless of the order in which the skills appear in the résumé.

---

## 3. Stage 3 — Finite automata

### 3.1 Structure

In this stage, I use finite automata to check whether the normalized qualifications match the requirements of each candidate profile.

Each automaton is organized as a sequence of stages. At each stage, the automaton can read one of several alternative qualifications and move to the next state. If a stage is optional, the automaton also has a λ transition that allows it to skip that stage.

The alphabet (\Sigma) contains canonical qualifications rather than individual characters because the input of this stage is the sequence produced by stage 2

### 3.2 Type of the automata

All four automata are non-deterministic finite automata. The transition relation is partial because each state only has transitions for the alternatives allowed at its corresponding stage. It is not defined for every possible symbol in the alphabet.

Some automata also include λ transitions to represent optional stages. In those cases, I use an epsilon-NFA, which allows transitions without consuming an input symbol. The other two automata do not need λ transitions, so they are regular NFAs


| Profile                     | Optional stage                       | Type   | \|Q\| | \|Σ\| | Transitions |
| --------------------------- | ------------------------------------ | ------ | ----- | ------ | ----------- |
| `FULL_STACK_DEVELOPER`      | API (`REST_API`)                     | NFA-λ | 7     | 13     | 14          |
| `MACHINE_LEARNING_ENGINEER` | ML_PRACTICE (`ML_MODEL_DEVELOPMENT`) | NFA-λ | 7     | 10     | 11          |
| `MOBILE_DEVELOPER`          | none                                 | NFA    | 6     | 14     | 14          |
| `DATA_ENGINEER`             | none                                 | NFA    | 6     | 11     | 11          |

I use EpsilonNFA for all four profiles. This lets me keep a consistent implementation, including for the profiles that do not use λ transitions.

### 3.3 `FULL_STACK_DEVELOPER`

M = (Q, Σ, δ, q₀, F) with

* Q = {q₀, q₁, q₂, q₃, q₄, q₅, q₆}
* Σ = {JAVASCRIPT, TYPESCRIPT, REACT, ANGULAR, VUE, NODE_JS, DJANGO,
  SPRING_BOOT, POSTGRESQL, SQL, NOSQL, REST_API, GIT}
* q₀ = q₀
* F = {q₆}
* δ:


|                           |                           |                            |
| ------------------------- | ------------------------- | -------------------------- |
| δ(q₀, JAVASCRIPT) = q₁ | δ(q₀, TYPESCRIPT) = q₁ |                            |
| δ(q₁, REACT) = q₂      | δ(q₁, ANGULAR) = q₂    | δ(q₁, VUE) = q₂         |
| δ(q₂, NODE_JS) = q₃    | δ(q₂, DJANGO) = q₃     | δ(q₂, SPRING_BOOT) = q₃ |
| δ(q₃, POSTGRESQL) = q₄ | δ(q₃, SQL) = q₄        | δ(q₃, NOSQL) = q₄       |
| δ(q₄, REST_API) = q₅   | δ(q₄, λ) = q₅         |                            |
| δ(q₅, GIT) = q₆        |                           |                            |

**Profile pattern.** A Full Stack Developer declares a front-end language,
a front-end framework, a back-end technology, a database, optionally an API
style, and version control. The API stage is optional because the assignment
itself accepts the sequence JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT as a
Full Stack Developer, and that sequence
contains no `REST_API`.

Diagram: `docs/diagrams/fa_FULL_STACK_DEVELOPER.dot|.png`.

### 3.4 `MACHINE_LEARNING_ENGINEER`

Q = {q₀ … q₆}, F = {q₆}, Σ of 10 symbols.


|                                     |                           |                        |
| ----------------------------------- | ------------------------- | ---------------------- |
| δ(q₀, PYTHON) = q₁               |                           |                        |
| δ(q₁, PANDAS) = q₂               | δ(q₁, NUMPY) = q₂      |                        |
| δ(q₂, SCIKIT_LEARN) = q₃         | δ(q₂, TENSORFLOW) = q₃ | δ(q₂, PYTORCH) = q₃ |
| δ(q₃, ML_MODEL_DEVELOPMENT) = q₄ | δ(q₃, λ) = q₄         |                        |
| δ(q₄, POSTGRESQL) = q₅           | δ(q₄, SQL) = q₅        |                        |
| δ(q₅, GIT) = q₆                  |                           |                        |

**Profile pattern.** Python, a data-handling library, a machine-learning
framework, optionally explicit model-development experience, a database and
version control. The first three stages and the last two reproduce the
automaton drawn of the assignment; the optional stage is additional
and does not change the language accepted by that example, since the example
accepts PYTHON, PANDAS, TENSORFLOW, POSTGRESQL, GIT.

Diagram: `docs/diagrams/fa_MACHINE_LEARNING_ENGINEER.dot|.png`.

### 3.5 `MOBILE_DEVELOPER`

Q = {q₀ … q₅}, F = {q₅}, no λ transitions.


|                            |                         |                             |
| -------------------------- | ----------------------- | --------------------------- |
| δ(q₀, KOTLIN) = q₁      | δ(q₀, SWIFT) = q₁    | δ(q₀, DART) = q₁         |
| δ(q₀, JAVA) = q₁        |                         |                             |
| δ(q₁, ANDROID_SDK) = q₂ | δ(q₁, FLUTTER) = q₂  | δ(q₁, REACT_NATIVE) = q₂ |
| δ(q₁, SWIFTUI) = q₂     |                         |                             |
| δ(q₂, SQLITE) = q₃      | δ(q₂, FIREBASE) = q₃ | δ(q₂, ROOM) = q₃         |
| δ(q₃, REST_API) = q₄    | δ(q₃, GRAPHQL) = q₄  |                             |
| δ(q₄, GIT) = q₅         |                         |                             |

**Profile pattern.** A mobile application developer writes the application
in a mobile language, builds the interface with a mobile framework, stores
data on the device, consumes a remote interface and uses version control.
Every stage is required, which is what separates this profile from
`FULL_STACK_DEVELOPER`: the two share no stage except version control.

Diagram: `docs/diagrams/fa_MOBILE_DEVELOPER.dot|.png`.

### 3.6 `DATA_ENGINEER`

Q = {q₀ … q₅}, F = {q₅}, no λ transitions.


|                         |                           |                      |
| ----------------------- | ------------------------- | -------------------- |
| δ(q₀, PYTHON) = q₁   | δ(q₀, SCALA) = q₁      |                      |
| δ(q₁, SPARK) = q₂    | δ(q₁, HADOOP) = q₂     | δ(q₁, KAFKA) = q₂ |
| δ(q₂, AIRFLOW) = q₃  | δ(q₂, DBT) = q₃        |                      |
| δ(q₃, BIGQUERY) = q₄ | δ(q₃, POSTGRESQL) = q₄ | δ(q₃, SQL) = q₄   |
| δ(q₄, GIT) = q₅      |                           |                      |

**Profile pattern.** A data engineer writes pipelines in a data language,
processes volume on a distributed platform, schedules the pipelines with an
orchestration tool, lands the result in an analytical store and uses version
control. The DATA_PLATFORM and ORCHESTRATION stages are what separate this
profile from `MACHINE_LEARNING_ENGINEER`, which shares PYTHON and the
database stage but requires a machine-learning framework instead.

Diagram: `docs/diagrams/fa_DATA_ENGINEER.dot|.png`.

### 3.7 Several profiles may be accepted

Nothing forces the four languages to be disjoint, and the assignment
explicitly speaks of "the result of the profile classification (for each
accepted profile)". `classifier.classify` therefore evaluates all
four automata and returns one verdict per profile.

---

## 4. Stage 4 — Candidate profile language

### 4.1 EBNF description

I use Extended Backus-Naur Form (EBNF) to describe the syntax of the candidate profile language. In this notation, writing elements next to each other represents a sequence, `|` represents a choice, `[ ]`represents an optional element, and`{ }` represents repetition.

```ebnf
candidate_profile ⇐ "candidate" string "{"
                      contact
                      [ "summary" string ]
                      [ "education" "{" { education_record } "}" ]
                      [ "experience" "{" { experience_record } "}" ]
                      "skills" "{" { qualification } "}"
                      evaluation { evaluation }
                    "}"

contact           ⇐ "contact" "{"
                      "email" email
                      [ "phone" string ]
                      [ "location" string ]
                      [ "role" string ]
                    "}"

education_record  ⇐ "degree" string "institution" string "year" integer

experience_record ⇐ "position" string "organization" string "years" integer
                    [ "responsibilities" "{" { string } "}" ]

evaluation        ⇐ "evaluation" profile_name "{"
                      "pattern" verdict
                      [ "sequence" "{" { qualification } "}" ]
                      [ "note" string ]
                    "}"

qualification     ⇐ uppercase_letter { uppercase_letter | digit | "_" }
profile_name      ⇐ uppercase_letter { uppercase_letter | digit | "_" }
verdict           ⇐ "ACCEPTED" | "REJECTED"
email             ⇐ local_part "@" domain "." top_level_domain
```

**Terminals.** `"candidate"`, `"contact"`, `"summary"`, `"education"`,
`"experience"`, `"skills"`, `"evaluation"`, `"email"`, `"phone"`,
`"location"`, `"role"`, `"degree"`, `"institution"`, `"year"`, `"position"`,
`"organization"`, `"years"`, `"responsibilities"`, `"pattern"`,
`"sequence"`, `"note"`, `"ACCEPTED"`, `"REJECTED"`, `"{"`, `"}"`, plus the
lexical classes `string`, `integer`, `uppercase_letter`, `digit` and the
components of `email`.

**Non-terminals.** `candidate_profile` (start symbol), `contact`,
`education_record`, `experience_record`, `evaluation`, `qualification`,
`profile_name`, `verdict`, `email`.

### 4.2 Main characteristics of the language

* **Hierarchical.** A candidate profile has a root block that contains smaller blocks. This allows me to represent the information in an organized way
* **Optionality.** Five constructs are optional (`summary`, `education`,
  `experience`, the three secondary contact fields, `sequence` and `note`),
  This is useful because stage 1 may not find all this information in every résumé.
* **Repetition.** Education records, experience entries, responsibilities, skills, and evaluations can appear multiple times. This allows the language to represent candidates with different amounts of information.
* **At least one evaluation.** A candidate profile must contain at least one evaluation block because a classification result is part of the output generated by ResumeLens.
* **Canonical qualification names.** Qualifications must be written in uppercase. For example, javascript is not valid in this language, even though it is a valid word, because stage 2 converts recognized qualifications into canonical forms.

### 4.3 Relation between the EBNF description and the textX grammar

The textX implementation is `src/dsl/candidate.tx`. The correspondence is
direct:


| EBNF                     | textX                                   |
| ------------------------ | --------------------------------------- |
| sequence (juxtaposition) | sequence (lecture 10, slide 46)         |
| `A/B`                    | `A/B`, ordered choice                   |
| `[ A ]`                  | `(A)?`, optional (slide 52)             |
| `{ A }`                  | `a*=A`, zero or more (slides 55 and 69) |
| one or more`A`           | `a+=A` (slide 69)                       |
| `string`, `integer`      | `STRING`, `INT` (slides 38-39)          |
| lexical class            | regular-expression match (slides 43-44) |

One detail I had to consider is that textX uses PEG parsing. In this type of parsing, the order of alternatives matters because the parser commits to the first alternative that succeeds, instead of exploring all alternatives as a general context-free grammar might.

The EBNF description represents the language at a formal level, while the textX grammar is the version I use in the implementation. In the relevant choices, the alternatives begin with different terminals, which helps avoid ambiguity.

### 4.4 Validation and rejection

I use `dsl.validate` to build the meta-model with `metamodel_from_file` and parses
with `model_from_str`. If a representation violates the grammar, textX raises a`TextXError`, which `dsl.is_valid` converts into a message.

I test the following invalid representations in `tests/test_dsl.py`:


| Violation                                 | Example                    | Kind      |
| ----------------------------------------- | -------------------------- | --------- |
| Qualification not in canonical form       | `skills { javascript }`    | lexical   |
| Qualification starting with an underscore | `skills { _GIT }`          | lexical   |
| Malformed e-mail                          | `email john.smith.example` | lexical   |
| Verdict outside the two allowed ones      | `pattern MAYBE`            | lexical   |
| Missing`skills` block                     | —                         | syntactic |
| No`evaluation` block                      | —                         | syntactic |
| Missing`contact` block                    | —                         | syntactic |
| Unclosed block                            | —                         | syntactic |
| Empty input                               | —                         | syntactic |

These tests allow me to check that the language does not accept representations that fail to follow the expected structure.

---

## 5. Diagrams

I generate all the diagrams automatically using `src/visualization/diagram_exporter.py`. The exporter creates DOT files, which I convert into PNG images using pydot and Graphviz.

The diagrams are stored in `docs/diagrams/`:


| Files                                   | What they show                                                                                                   |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `fst_<category>.dot` / `.png`, 12 pairs | The prefix tree of each transducer, edges labelled`input:output`                                                 |
| `fa_<profile>.dot` / `.png`, 4 pairs    | The transition diagram of each automaton, with the alternatives of each stage grouped on the corresponding edge. |

I chose to generate the diagrams instead of drawing them manually because some transducers contain many states and transitions. Generating them from the code makes the process easier and helps ensure that the diagrams match the models they represent. Whenever I modify a formal model, I can generate the diagrams again instead of updating them by hand.
