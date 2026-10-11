QUALIFICATION_VARIANTS = {
    "LANGUAGE": {
        "JAVASCRIPT": ["JS", "Javascript", "JavaScript"],
        "TYPESCRIPT": ["TS", "Typescript", "TypeScript"],
        "PYTHON": ["Python", "python", "Python3"],
        "JAVA": ["Java", "java"],
        "KOTLIN": ["Kotlin", "kotlin"],
        "SWIFT": ["Swift", "swift"],
        "DART": ["Dart", "dart"],
        "SCALA": ["Scala", "scala"],
    },
    "FRONTEND": {
        "REACT": ["React", "React.js", "ReactJS"],
        "ANGULAR": ["Angular", "AngularJS"],
        "VUE": ["Vue", "Vue.js", "VueJS"],
    },
    "BACKEND": {
        "NODE_JS": ["NodeJS", "Node.js", "Node"],
        "DJANGO": ["Django", "django"],
        "SPRING_BOOT": ["Spring Boot", "SpringBoot", "Spring"],
    },
    "DATABASE": {
        "POSTGRESQL": ["Postgres", "PostgreSQL", "postgres"],
        "NOSQL": ["NoSQL", "NOSQL", "No SQL"],
        "BIGQUERY": ["BigQuery", "Big Query", "bigquery"],
        "SQL": ["SQL", "sql"],
    },
    "DATA_LIBRARY": {
        "PANDAS": ["pandas", "Pandas"],
        "NUMPY": ["numpy", "NumPy", "Numpy"],
    },
    "ML_FRAMEWORK": {
        "SCIKIT_LEARN": ["sklearn", "scikit learn", "Scikit-learn"],
        "TENSORFLOW": ["TensorFlow", "Tensor Flow", "tensorflow"],
        "PYTORCH": ["PyTorch", "Py Torch", "pytorch"],
        "ML_MODEL_DEVELOPMENT": [
            "Machine-learning model development",
            "Machine learning model development",
        ],
    },
    "API": {
        "REST_API": ["REST APIs", "REST API", "RESTful APIs"],
        "GRAPHQL": ["GraphQL", "graphql", "Graph QL"],
    },
    "MOBILE_FRAMEWORK": {
        "ANDROID_SDK": ["Android SDK", "Android", "AndroidSDK"],
        "FLUTTER": ["Flutter", "flutter"],
        "REACT_NATIVE": ["React Native", "ReactNative"],
        "SWIFTUI": ["SwiftUI", "Swift UI"],
    },
    "MOBILE_STORAGE": {
        "SQLITE": ["SQLite", "sqlite", "SQLite3"],
        "FIREBASE": ["Firebase", "firebase"],
        "ROOM": ["Room", "Room Database"],
    },
    "DATA_PLATFORM": {
        "SPARK": ["Spark", "Apache Spark", "PySpark"],
        "HADOOP": ["Hadoop", "Apache Hadoop"],
        "KAFKA": ["Kafka", "Apache Kafka"],
    },
    "ORCHESTRATION": {
        "AIRFLOW": ["Airflow", "Apache Airflow", "airflow"],
        "DBT": ["dbt", "DBT", "Data Build Tool"],
    },
    "VERSION_CONTROL": {
        "GIT": ["Git", "git", "GIT"],
    },
}


def category_names():
    """Return the names of the qualification categories.

    There is exactly one finite-state transducer per category.
    """
    return list(QUALIFICATION_VARIANTS.keys())


def canonical_qualifications():
    """Return every canonical qualification known to the system."""
    result = []
    for canonical_forms in QUALIFICATION_VARIANTS.values():
        for canonical in canonical_forms:
            if canonical not in result:
                result.append(canonical)
    return result


def category_of(canonical):
    """Return the category a canonical qualification belongs to, or None."""
    for category, canonical_forms in QUALIFICATION_VARIANTS.items():
        if canonical in canonical_forms:
            return category
    return None