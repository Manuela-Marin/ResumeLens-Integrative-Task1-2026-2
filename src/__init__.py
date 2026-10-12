"""ResumeLens: resume screening based on formal language models.

Integrative Task 1, Computación y Estructuras Discretas III, 2026-2.

    ingestion       reads the resume from disk
    extraction      stage 1, regular expressions
    normalization   stage 2, finite-state transducers
    classification  stage 3, finite automata
    dsl             stage 4, candidate profile language

plus `profiles`, which holds the definition of the four professional
profiles as data, and the output modules `visualization` and `main`.
"""