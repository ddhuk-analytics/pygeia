"""data setup"""
import pytest
from fms.preprocess import TechnicalText


@pytest.fixture(name="data")
def raw_data():
    """Return a raw text instance"""
    return {
        0: {
            "TASK_DESCRIPTION": "c/o seal in 1PK-1234",
            "PROBLEM_CODE": "UNK",
            "PROBLEM_CODE_TEXT": "UNKNOWN, PLEASE SPECIFY",
            "PROBLEM_NOTE": (
                "Ladder cylinder rods corroded very bad causing damage to rod seals."
            ),
            "CAUSE_CODE": "INSERR",
            "CAUSE_CODE_TEXT": "Installation Error",
            "CAUSE_NOTE": (
                "No protective boots installed over cylinder rods allowing dust & dirt."
            ),
        },
    }


@pytest.fixture(name="text_cols")
def text_columns():
    "Return colunm names of raw text"
    return ["TASK_DESCRIPTION", "PROBLEM_NOTE", "CAUSE_NOTE"]


@pytest.fixture(name="context_cols")
def context_columns():
    "Return colunm names of raw text"
    return ["PROBLEM_CODE", "PROBLEM_CODE_TEXT", "CAUSE_CODE", "CAUSE_CODE_TEXT"]


@pytest.fixture()
def technical_text(data, text_cols, context_cols):
    "Return a TechnicalText instance"
    return TechnicalText(data, text_cols, context_cols)


@pytest.fixture()
def expected_text():
    """Return the expected text instance"""
    return [
        "c/o seal in 1pk-1234",
        "ladder cylinder rods corroded very bad causing damage to rod seals.",
        "no protective boots installed over cylinder rods allowing dust & dirt.",
    ]


@pytest.fixture()
def expected_context():
    """Return the expected context instance"""
    return [
        {
            "index": 0,
            "header": "TASK_DESCRIPTION",
            "PROBLEM_CODE": "UNK",
            "PROBLEM_CODE_TEXT": "UNKNOWN, PLEASE SPECIFY",
            "CAUSE_CODE": "INSERR",
            "CAUSE_CODE_TEXT": "Installation Error",
        },
        {
            "index": 0,
            "header": "PROBLEM_NOTE",
            "PROBLEM_CODE": "UNK",
            "PROBLEM_CODE_TEXT": "UNKNOWN, PLEASE SPECIFY",
            "CAUSE_CODE": "INSERR",
            "CAUSE_CODE_TEXT": "Installation Error",
        },
        {
            "index": 0,
            "header": "CAUSE_NOTE",
            "PROBLEM_CODE": "UNK",
            "PROBLEM_CODE_TEXT": "UNKNOWN, PLEASE SPECIFY",
            "CAUSE_CODE": "INSERR",
            "CAUSE_CODE_TEXT": "Installation Error",
        },
    ]
