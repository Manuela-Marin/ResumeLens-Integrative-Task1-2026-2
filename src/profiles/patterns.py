PROFILE_PATTERNS = {
    "FULL_STACK_DEVELOPER": [
        {"stage": "LANGUAGE",
         "alternatives": ["JAVASCRIPT", "TYPESCRIPT"], "required": True},
        {"stage": "FRONTEND",
         "alternatives": ["REACT", "ANGULAR", "VUE"], "required": True},
        {"stage": "BACKEND",
         "alternatives": ["NODE_JS", "DJANGO", "SPRING_BOOT"], "required": True},
        {"stage": "DATABASE",
         "alternatives": ["POSTGRESQL", "SQL", "NOSQL"], "required": True},
        {"stage": "API",
         "alternatives": ["REST_API"], "required": False},
        {"stage": "VERSION_CONTROL",
         "alternatives": ["GIT"], "required": True},
    ],

    "MACHINE_LEARNING_ENGINEER": [
        {"stage": "LANGUAGE",
         "alternatives": ["PYTHON"], "required": True},
        {"stage": "DATA_LIBRARY",
         "alternatives": ["PANDAS", "NUMPY"], "required": True},
        {"stage": "ML_FRAMEWORK",
         "alternatives": ["SCIKIT_LEARN", "TENSORFLOW", "PYTORCH"],
         "required": True},
        {"stage": "ML_PRACTICE",
         "alternatives": ["ML_MODEL_DEVELOPMENT"], "required": False},
        {"stage": "DATABASE",
         "alternatives": ["POSTGRESQL", "SQL"], "required": True},
        {"stage": "VERSION_CONTROL",
         "alternatives": ["GIT"], "required": True},
    ],

    "MOBILE_DEVELOPER": [
        {"stage": "LANGUAGE",
         "alternatives": ["KOTLIN", "SWIFT", "DART", "JAVA"], "required": True},
        {"stage": "MOBILE_FRAMEWORK",
         "alternatives": ["ANDROID_SDK", "FLUTTER", "REACT_NATIVE", "SWIFTUI"],
         "required": True},
        {"stage": "MOBILE_STORAGE",
         "alternatives": ["SQLITE", "FIREBASE", "ROOM"], "required": True},
        {"stage": "API",
         "alternatives": ["REST_API", "GRAPHQL"], "required": True},
        {"stage": "VERSION_CONTROL",
         "alternatives": ["GIT"], "required": True},
    ],

    "DATA_ENGINEER": [
        {"stage": "LANGUAGE",
         "alternatives": ["PYTHON", "SCALA"], "required": True},
        {"stage": "DATA_PLATFORM",
         "alternatives": ["SPARK", "HADOOP", "KAFKA"], "required": True},
        {"stage": "ORCHESTRATION",
         "alternatives": ["AIRFLOW", "DBT"], "required": True},
        {"stage": "DATABASE",
         "alternatives": ["BIGQUERY", "POSTGRESQL", "SQL"], "required": True},
        {"stage": "VERSION_CONTROL",
         "alternatives": ["GIT"], "required": True},
    ],
}


def profile_names():
    """Return the names of the four supported professional profiles."""
    return list(PROFILE_PATTERNS.keys())


def stages_of(profile_name):
    """Return the ordered list of stages of one profile."""
    return PROFILE_PATTERNS[profile_name]