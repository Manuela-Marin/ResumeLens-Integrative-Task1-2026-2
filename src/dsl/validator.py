import os

from textx import metamodel_from_file
from textx.exceptions import TextXError

GRAMMAR_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "candidate.tx")
_META_MODEL = None


def meta_model():
    """Return the textX meta-model of the candidate profile language."""
    global _META_MODEL
    if _META_MODEL is None:
        _META_MODEL = metamodel_from_file(GRAMMAR_PATH)
    return _META_MODEL


def validate(text):
    """Parse a sentence of the language and return the textX model."""
    return meta_model().model_from_str(text)


def validate_file(path):
    """Parse a candidate profile stored on disk and return the textX model."""
    return meta_model().model_from_file(path)


def is_valid(text):
    """Return a pair (valid, message)."""
    try:
        validate(text)
    except TextXError as error:
        return False, str(error)
    return True, "The candidate profile is a valid sentence of the language."