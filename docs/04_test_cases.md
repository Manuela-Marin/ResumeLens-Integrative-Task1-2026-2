# Test case design

This section corresponds to deliverable 2c of the assignment. Here, I describe the test cases I designed for the project, including the different situations I want to check and the results I expect from each one.

I organized the tests according to the four stages of the system. I also included tests for the formal definitions, the classification of candidates, and the generation and validation of the DSL.

I wrote this document as the plan for the test suite, before recording the results of running the tests. Once the tests are implemented and executed, I can add the actual results at the end.

I will keep the tests in the `tests/` directory, with a separate file for each stage. To run them from the root of the repository, I use:

```bash
python -m unittest discover -s tests -t .
```

I chose `unittest` because it is included in Python's standard library, so I do not need to install another dependency. Since the course material does not cover a specific testing framework, this seemed like a simple way to implement the required tests.

---

## 1. End-to-end scenarios

I defined five scenarios to check how the complete system behaves with different résumés. Each scenario uses one of the files in `data/resumes/`.


| #  | Scenario                                                           | Résumé               | Expected outcome                                                               |
| -- | ------------------------------------------------------------------ | ---------------------- | ------------------------------------------------------------------------------ |
| S1 | Candidate matching reference profile 1                             | `wednesday_addams.txt` | `FULL_STACK_DEVELOPER` is accepted, and the other three profiles are rejected. |
| S2 | Candidate matching reference profile 2                             | `mary_jane_watson.txt` | `MACHINE_LEARNING_ENGINEER` is accepted.                                       |
| S3 | Candidate matching the additional software engineering profile     | `miles_morales.txt`    | `MOBILE_DEVELOPER` is accepted.                                                |
| S4 | Candidate matching the additional AI and data profile              | `shuri_udaku.txt`      | `DATA_ENGINEER` is accepted.                                                   |
| S5 | Candidate that does not match any profile and has an unknown skill | `bruce_banner.txt`     | No profile is accepted, and`Fortran` is reported as unrecognized.              |

I chose these five scenarios because they let me test both profiles provided in the assignment and the two additional profiles I defined for the project. They also let me check what happens when a candidate does not meet the requirements of any profile.

The first two scenarios are based on the examples in the assignment. I use Wednesday Addams to check whether the extraction results match the information shown and whether the qualifications are ordered as expected. For Mary Jane Watson, I check whether the automaton accepts the sequence specified for the Machine Learning Engineer profile.

---

## 2. Stage 1 — Extraction (`tests/test_extraction.py`)

For the first stage, I designed tests to check whether the regular expressions can identify the information in a résumé. I also included cases where some information is missing, so I can verify that the program handles those situations correctly.


| Case                                     | Input                                     | Expected result                                                                  |
| ---------------------------------------- | ----------------------------------------- | -------------------------------------------------------------------------------- |
| Name                                     | Wednesday Addams's résumé               | `Wednesday Addams`                                                               |
| E-mail                                   | Wednesday Addams's résumé               | `wednesday.addams@example.com`                                                   |
| Telephone                                | Wednesday Addams's résumé               | `300-555-123`                                                                    |
| Different telephone formats              | `555-555-555`, `555 555 555`, `555555555` | All three formats are recognized, as practiced in lecture 3, slide 28.           |
| Location and role                        | Wednesday Addams's résumé               | Both fields are extracted.                                                       |
| Missing fields                           | A résumé containing only a name         | Missing values return`None` instead of raising an exception.                     |
| Summary                                  | Wednesday Addams's résumé               | The summary paragraph is returned as one line.                                   |
| Missing summary                          | A résumé containing only a name         | `None` is returned.                                                              |
| Education                                | Wednesday Addams's résumé               | `BSc`, `Computer Science`, `Nevermore Academy`, `2024`.                          |
| Missing education section                | A résumé containing only a name         | An empty list is returned.                                                       |
| Experience                               | Wednesday Addams's résumé               | The title, organization, years, and two responsibilities are extracted.          |
| Total experience                         | Wednesday Addams's résumé               | `3`                                                                              |
| Raw skills                               | Wednesday Addams's résumé               | `JS`, `React.js`, `NodeJS`, `Postgres`, `Git`.                                   |
| **Extraction does not normalize skills** | Wednesday Addams's résumé               | `JS` is present, but `JAVASCRIPT` is not. This follows the separation described. |
| Missing skills section                   | A résumé containing only a name         | An empty list is returned.                                                       |
| Keys returned by`extract`                | Wednesday Addams's résumé               | The dictionary contains the ten expected keys.                                   |

I included the case about raw skills because I want to make sure that extraction and normalization remain separate. The first stage should preserve the way skills appear in the résumé; converting them to canonical forms belongs to the next stage.

---

## 3. Stage 2 — Normalization (`tests/test_normalization.py`)

For normalization, I designed tests for both the formal definition of the transducers and the way they convert skill names. I also included cases involving unknown skills, duplicate qualifications, and names that are similar to each other.

### Structure of the 7-tuple


| Case                                       | Expected result                                                                                             |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| All seven components are present           | Every category has the complete 7-tuple.                                                                    |
| \(q_0 \in Q\)                              | The initial state belongs to the set of states for every category.                                          |
| \(F \neq \emptyset\) and \(F \subseteq Q\) | The final-state set is non-empty and contains only states from\(Q\), as covered in lectures 6–7, slide 18. |
| \(\Gamma\) contains the canonical forms    | For`T_FRONTEND`, the output alphabet includes `{REACT, ANGULAR, VUE}`.                                      |
| Every transition connects states in\(Q\)   | All transitions use states defined for the corresponding category.                                          |

### Transductions


| Case                                   | Input                                                                                                                                                                                             | Expected result                                                                                                                          |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Examples from the assignment           | `JS`, `Javascript`, `React.js`, `ReactJS`, `NodeJS`, `Node.js`, `Postgres`, `PostgreSQL`, `pandas`, `sklearn`, `scikit learn`, `Scikit-learn`, `Tensor Flow`, `TensorFlow`, `Py Torch`, `PyTorch` | Each recognized variant produces the canonical form specified.                                                                           |
| Variants containing spaces             | `Spring Boot`, `Apache Spark`, `Big Query`, `Android SDK`                                                                                                                                         | `SPRING_BOOT`, `SPARK`, `BIGQUERY`, `ANDROID_SDK`. I included these to check the character-level approach used to build the transducers. |
| **One variant is a prefix of another** | `Java`/`JavaScript`, `Swift`/`SwiftUI`, `React`/`React Native`, `Room`/`Room Database`                                                                                                            | Each variant keeps its own canonical form, without concatenating outputs from different matches.                                         |
| Unknown qualifications                 | `Fortran`, `COBOL`, `""`                                                                                                                                                                          | `None` is returned.                                                                                                                      |
| Duplicates and unknown skills          | `JS`, `Javascript`, `Git`, `Fortran`                                                                                                                                                              | Canonical qualifications:`[JAVASCRIPT, GIT]`; unknown skills: `[Fortran]`.                                                               |
| Example from the assignment            | `JS`, `React.js`, `NodeJS`, `Postgres`, `Git`                                                                                                                                                     | `JAVASCRIPT`, `REACT`, `NODE_JS`, `POSTGRESQL`, `GIT`.                                                                                   |

I included the prefix cases because some skill names start with the same characters. I want to verify that recognizing one variant does not accidentally produce an incorrect result for another.

I also check duplicate and unknown skills to make sure that normalization returns the recognized qualifications without repeating equivalent skills, while keeping the unknown ones separate.

### Canonical ordering

After normalization, I need to check that the qualifications follow the order defined by the profile rather than the order in which they appeared in the résumé.


| Case                             | Input                                     | Expected result                                                           |
| -------------------------------- | ----------------------------------------- | ------------------------------------------------------------------------- |
| Sequence shown in the assignment | `Git, NodeJS, JS, Postgres, React.js`     | `JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT`, as shown.                  |
| Independence from résumé order | The same skills in two different orders   | Both inputs produce the same ordered sequence.                            |
| One qualification per stage      | A candidate with both`PANDAS` and `NUMPY` | The resulting sequence contains exactly one qualification for that stage. |

These cases help me check that the output is consistent even when candidates write their skills in different orders.

---

## 4. Stage 3 — Classification (`tests/test_classification.py`)

For classification, I designed tests to check the formal definition of each automaton, its type, and whether it accepts or rejects different sequences of qualifications.

### Structure of the 5-tuple


| Case                              | Expected result                                                                    |
| --------------------------------- | ---------------------------------------------------------------------------------- |
| All five components are present   | Every profile has the complete 5-tuple.                                            |
| \(q_0\) and \(F\) belong to \(Q\) | The initial state and every final state belong to the set of states.               |
| \(F \neq \emptyset\)              | Every automaton has at least one final state, as required by lecture 3, slide 115. |
| \(                                | Q                                                                                  |
| **\(\delta\) is partial**         | The number of defined`(state, symbol)` pairs is smaller than \(                    |

### Automaton type

I also check that the type of automaton matches the stages defined for each profile.


| Case                                  | Expected result                                                          |
| ------------------------------------- | ------------------------------------------------------------------------ |
| Profile with an optional stage        | `FULL_STACK_DEVELOPER` and `MACHINE_LEARNING_ENGINEER` use `NFA-lambda`. |
| Profile where every stage is required | `MOBILE_DEVELOPER` and `DATA_ENGINEER` use `NFA`.                        |

### Acceptance


| Case                                    | Input                                                                       | Expected result                |
| --------------------------------------- | --------------------------------------------------------------------------- | ------------------------------ |
| Example from the assignment             | `PYTHON, PANDAS, TENSORFLOW, POSTGRESQL, GIT` for Machine Learning Engineer | Accepted, as shown.            |
| Full Stack sequence from the assignment | `JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT`                               | Accepted.                      |
| Optional stage included                 | The same Full Stack sequence plus`REST_API`                                 | Accepted.                      |
| Required stage missing                  | Full Stack sequence without a database qualification                        | Rejected.                      |
| Empty sequence                          | `[]`                                                                        | Rejected by all four automata. |
| Qualifications in the wrong order       | A sequence starting with`GIT`                                               | Rejected.                      |

I included both accepted and rejected sequences because I want to check that the automata do not accept every candidate by default. The qualifications must satisfy the required stages and their order.

### Classification of the five scenarios


| Case                        | Expected result                                                             |
| --------------------------- | --------------------------------------------------------------------------- |
| S1 — Wednesday Addams      | Only`FULL_STACK_DEVELOPER` is accepted.                                     |
| S2 — Mary Jane Watson      | `MACHINE_LEARNING_ENGINEER` is among the accepted profiles.                 |
| S3 — Miles Morales         | `MOBILE_DEVELOPER` is among the accepted profiles.                          |
| S4 — Shuri Udaku           | `DATA_ENGINEER` is among the accepted profiles.                             |
| S5 — Bruce Banner          | No profile is accepted.                                                     |
| All profiles are evaluated  | Four results are returned, following the order of`profile_names()`.         |
| Missing stages are reported | Every rejected result includes the required stages that were not satisfied. |

These tests let me verify that the classifier evaluates all four profiles using the same general implementation and explains why a candidate is rejected.

---

## 5. Stage 4 — DSL and visualization (`tests/test_dsl.py`)

For the last stage, I designed tests to check whether the candidate profiles follow the grammar defined in textX. I also included invalid inputs and tests for the HTML and Markdown outputs.

### Valid profiles


| Case                       | Expected result                                                                     |
| -------------------------- | ----------------------------------------------------------------------------------- |
| Sentence generated from S1 | The generated profile belongs to the language.                                      |
| Minimal profile            | A profile containing the minimum required information belongs to the language.      |
| Model content              | The model contains the candidate's name, e-mail, five skills, and four evaluations. |
| Comments                   | A line comment is ignored, as covered in lecture 11, slide 14.                      |

### Lexical rejection

Here, I check that the grammar does not accept values that do not follow the expected format.


| Case                                      | Example                    |
| ----------------------------------------- | -------------------------- |
| Qualification not in canonical form       | `skills { python GIT }`    |
| Invalid e-mail format                     | `email john.smith.example` |
| Verdict outside the allowed values        | `pattern MAYBE`            |
| Qualification starting with an underscore | `skills { _PYTHON }`       |

### Syntactic rejection

I also check that the validator rejects profiles that are incomplete or do not follow the grammar's structure.


| Case                        |
| --------------------------- |
| Missing`skills` block.      |
| Missing`evaluation` block.  |
| Missing`contact` block.     |
| A block that is not closed. |
| Empty input.                |

### Visualization


| Case                      | Expected result                                                |
| ------------------------- | -------------------------------------------------------------- |
| HTML sections             | The HTML contains the sections defined in`OutputExample.html`. |
| Normalized skills in HTML | The five canonical qualifications are displayed.               |
| Accepted profile in HTML  | `Full Stack Developer` and `ACCEPTED` are displayed.           |
| Markdown output           | The title and skills section are present.                      |
| HTML escaping             | The text`&"x"` is converted to `<b>&"x"`.                      |

I included the HTML escaping case because some résumé information may contain characters that have a special meaning in HTML. I want to make sure that the output displays those characters safely instead of interpreting them as HTML tags.

---

## 6. Coverage of the assignment requirements

I organized the tests so that I can check the main requirements of the assignment in each part of the project.


| Assignment requirement                    | Where it is covered             |
| ----------------------------------------- | ------------------------------- |
| extraction using regular expressions      | Section 2 — Extraction         |
| 7-tuple of each transducer                | Section 3 — Structure          |
| required transformations                  | Section 3 — Transductions      |
| canonical ordering                        | Section 3 — Canonical ordering |
| 5-tuple of each automaton                 | Section 4 — Structure          |
| automaton type                            | Section 4 — Automaton type     |
| classification into the four profiles     | Section 4 — Classification     |
| valid candidate profiles                  | Section 5 — Valid profiles     |
| rejection of lexical and syntactic errors | Section 5 — Rejection          |
| HTML or Markdown visualization            | Section 5 — Visualization      |

This organization helps me check that the tests cover the different parts of the assignment, instead of testing only whether the program runs without errors.

---

## 7. Results of test execution

```
$ python -m unittest discover -s tests -t .
....................................................................
----------------------------------------------------------------------
Ran 68 tests in 0.041s

OK
```


| File                           | Tests  |
| ------------------------------ | ------ |
| `tests/test_extraction.py`     | 16     |
| `tests/test_normalization.py`  | 14     |
| `tests/test_classification.py` | 20     |
| `tests/test_dsl.py`            | 18     |
| **Total**                      | **68** |
