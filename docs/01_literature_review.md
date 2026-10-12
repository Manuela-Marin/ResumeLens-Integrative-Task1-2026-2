# Literature Review

Before implementing ResumeLens, I reviewed existing work related to the main ideas behind the project. This helped me understand the available approaches, avoid using tools that would replace the work I was expected to develop, and make better decisions during implementation. I focused on three main topics: automated résumé screening, finite-state transducers for text normalization, and grammars and domain-specific languages. I also reviewed the tools used in the project and how the literature influenced my design decisions.

---

## 1. Automated Résumé Screening

Résumé screening involves checking whether a candidate has the qualifications required for a job. There are different ways to automate this process, but two common approaches are machine learning and rule-based methods.

Machine-learning approaches use examples of previous résumés to classify or rank candidates. They can identify information written in different ways, but they usually require training data. Their results can also be difficult to explain because the model learns patterns from the examples it receives. If previous hiring decisions contain biases, the model may reproduce them.

Rule-based approaches work differently. Instead of learning from examples, they use predefined rules to recognize information and check whether it meets certain requirements. One advantage is that their decisions are easier to explain because each result can be linked to a specific rule. However, these systems can only recognize the patterns that have been defined in advance.

For ResumeLens, I chose a rule-based approach because it fits the objective of the project. The system does not rank candidates or make hiring decisions. Instead, it checks whether the qualifications identified in a résumé match formally defined patterns. I considered formal language models more appropriate for this task because they allow me to represent these patterns and check whether the input satisfies them.

I also considered whether to use existing résumé-parsing and natural-language-processing libraries. Although these tools could make implementation easier, they would replace some of the steps I am expected to develop. Since the goal is to apply formal language concepts to the problem, I decided to implement the recognition and normalization stages myself.

Another issue I identified is that the same qualification can be written in different ways. For example, JavaScript, Javascript, and JS may refer to the same skill. Similarly, Scikit-learn, sklearn, and scikit learn can refer to the same tool. Because of this, I decided to keep recognition and normalization as separate stages.

This separation is important because recognizing a qualification and determining whether two expressions represent the same thing are different tasks. I first identify the information written in the résumé and then normalize the skills into their canonical forms.

---

## 2. Finite-State Transducers for Text Normalization

Finite-state transducers are used to transform an input into an output according to a set of defined transitions. They are commonly used in computational morphology, where they can relate a word to its base form or to information about its grammatical structure.

Mohri (1997) explains how finite-state transducers are used in language processing and discusses properties that make them useful for these tasks. For example, transducers can be combined through composition and can be determinized and minimized under the appropriate conditions. Beesley and Karttunen (2003) provide further examples of how finite-state methods can be used to build morphological analyzers. Jurafsky and Martin also discuss these methods in their treatment of morphology.

I connected these concepts with the examples studied in class. In these examples, transducers map words to morphological information or relate an infinitive, such as llorar, to its conjugated forms. They helped me understand how transitions can process an input and produce a corresponding output.

For ResumeLens, I applied the same general idea to qualifications. Instead of processing word forms or verb conjugations, I use transducers to recognize different ways of writing a skill and produce its canonical form. This allows the program to represent equivalent qualifications consistently before comparing them.

Two decisions in my implementation were influenced by these examples.

Output through a lambda transition. I used a lambda transition to produce the canonical form after recognizing the complete input. This is useful when one qualification is a prefix of another, such as Java and JavaScript, because I need to distinguish between the two.

Using a prefix tree. I chose a prefix-tree structure because different expressions can share states when they begin with the same characters. This avoids repeating transitions for prefixes that several qualifications have in common and makes the transducers easier to organize.

In ResumeLens, this structure allows me to represent multiple qualification variants without creating a completely independent path for every expression. It also makes the representation easier to maintain when I need to add or modify variants.

---

## 3. Grammars and Domain-Specific Languages

Another part of ResumeLens is the representation of a candidate's qualifications in a structured format. To implement this, I use a small language with its own syntax and rules. This is related to the concept of domain-specific languages (DSLs).

Fowler (2010) defines a DSL as a programming language with limited expressiveness that focuses on a particular domain. Fowler distinguishes between external DSLs, which have their own syntax and require a parser, and internal DSLs, which are expressed using an existing programming language.

I chose an external DSL for stage 4 because the candidate profile needs to follow a specific structure and be checked before it is used by the program. The language has its own grammar and is parsed using textX.

One reason for this decision is that I wanted to separate the information produced by the previous stages from the process of displaying it. Without a defined language, the program could send the results directly to the HTML generator, but it would be harder to ensure that the data follows the expected structure. By using a DSL, I can reject invalid representations before displaying them.

I use the grammar not only to organize the data but also to validate its structure. This means that the program can check whether a candidate profile follows the expected syntax instead of assuming that every generated or manually written representation is correct.

I used Extended Backus-Naur Form (EBNF) to describe the grammar because it allows me to define the syntax of the candidate profile language. The grammar documented in docs/03_formalization.md uses four main forms: sequence, choice, option, and repetition. These forms allow me to specify the order of elements and determine which parts of a candidate profile are required or optional.

I also considered an important detail about the parser. TextX uses PEG parsing, where the order of alternatives can affect how an expression is interpreted. This differs from the way alternatives are handled in a general context-free grammar. In the relevant parts of my grammar, alternatives begin with different terminals, which helps reduce the possibility of ambiguity. However, I still need to consider this difference when defining the grammar so that it works correctly with textX.

---

## 4. Tools Used in the Project

I selected `pyformlang` and `textX` to implement the formal language concepts, along with tools for creating the diagrams required by the assignment.

### Pyformlang

Romero (2021) describes `pyformlang` as a Python library designed for working with formal languages and automata. It supports regular expressions, finite automata, finite-state transducers, context-free grammars, push-down automata, and other related concepts.

I chose this library because its API follows the mathematical concepts studied in class. For example, an automaton can be represented using its states, alphabet, transition function, initial state, and final states. This makes it easier for me to connect the implementation with the theoretical models required by the assignment.

Since the project focuses on applying formal language theory, I considered `pyformlang` more appropriate than a general-purpose tool that hides the underlying implementation.

### TextX

I use textX to implement the grammar of the candidate profile language. Dejanović et al. (2017) describe textX as a tool for implementing domain-specific languages in Python. It uses a grammar to parse input and create objects that represent the resulting model.

I selected textX because it allows me to work with structured objects instead of processing the entire candidate profile as plain text. In lecture 11, the course presents an example in which a robot model is accessed through `model.commands`. I used this example as a reference for understanding how a parsed model can be accessed and processed. In ResumeLens, I apply the same general idea to the candidate profile and its visualization.

### Diagram Tools

The project includes graphical representations of the transducers and transition diagrams for the automata. Since these models contain many states and transitions, I decided to generate all the diagrams automatically from the implementation.

I use diagram_exporter to generate the diagrams in DOT format and pydot and Graphviz to convert them into PNG images. This avoids drawing the diagrams manually and helps ensure that they represent the models defined in the code. It also makes future changes easier to manage because the diagrams can be generated again after modifying the formal models.

If Graphviz is not installed locally, the generated DOT descriptions can also be used with GraphvizOnline to visualize the diagrams.

---

## 5. Design Decisions Based on the Literature Review

After reviewing the literature and the course materials, I made several decisions for ResumeLens. The following table summarizes the main decisions and the reasons behind them.


| Design decision                                             | Reason                                                                                                                                          |
| ----------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Use rule-based methods instead of machine learning          | I need to check qualifications against formally defined patterns rather than rank candidates or predict hiring outcomes.                        |
| Avoid résumé-parsing and NLP libraries                    | I need to implement the recognition and normalization stages myself using formal language concepts.                                             |
| Separate recognition from normalization                     | Recognizing a qualification and determining which expressions are equivalent are different tasks. The assignment also requires this separation. |
| Use character-level transducers organized as prefix trees   | This structure allows me to recognize different variants while sharing transitions between expressions with common prefixes.                    |
| Produce the canonical form through a lambda transition      | I applied this construction from class to help distinguish qualifications where one name is a prefix of another.                                |
| Use an external DSL for candidate profiles                  | I need a defined structure that allows me to validate the candidate profile before displaying it.                                               |
| Define the grammar in EBNF and implement it with textX      | I use EBNF to describe the language rules and textX to parse and validate candidate profiles.                                                   |
| Generate all diagrams automatically from the implementation | This avoids manual drawing and helps keep the diagrams consistent with the formal models in the code.                                           |

Overall, this review helped me understand how the theoretical concepts studied in class can be applied to ResumeLens. It also helped me choose the tools and structures that best fit the project. By keeping the recognition, normalization, and validation stages separate, I can organize the implementation more clearly and explain the role of each formal model in the program.

---

## References

Beesley, K. R., & Karttunen, L. (2003). *Finite State Morphology*. CSLI Publications.

Dejanović, I., Vaderna, R., Milosavljević, G., & Vuković, Ž. (2017). TextX: A Python tool for Domain-Specific Languages implementation. *Knowledge-Based Systems, 115*, 1–4. https://doi.org/10.1016/j.knosys.2016.10.023

Fowler, M. (2010). *Domain-Specific Languages*. Addison-Wesley.

Hopcroft, J. E., Motwani, R., & Ullman, J. D. (2006). *Introduction to Automata Theory, Languages, and Computation* (3rd ed.). Pearson.

Jurafsky, D., & Martin, J. H. *Speech and Language Processing*. Chapter on morphology and finite-state transducers.

Mohri, M. (1997). Finite-State Transducers in Language and Speech Processing. *Computational Linguistics, 23*(2), 269–311.

Romero, J. (2021). Pyformlang: An Educational Library for Formal Language Manipulation. In *Proceedings of the 52nd ACM Technical Symposium on Computer Science Education (SIGCSE 2021)* (pp. 576–582). ACM. https://doi.org/10.1145/3408877.3432464

Aristizábal P., A. A. (2026). *Computación y Estructuras Discretas III*, lecture slides 1–16, course 09772. Universidad Icesi.
