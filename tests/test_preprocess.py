"""preprocess module testing"""
import re
import pytest
from fms.constants import ID_PATTERN
from fms.preprocess import TechnicalText

testdata = {
    0: {
        "TASK": "C/O seal in 1pk-1234",
        "CODE": "UNK",
        "CODE_TEXT": "UNKNOWN",
        "PROBLEM": "corrosion",
    }
}


@pytest.mark.parametrize(
    "tdata, text, context, error, expected",
    [
        ({}, [], [], ValueError, "empty dictionary"),
        (testdata, ["TSK"], ["CODE", "CODE_TEXT"], RuntimeError, "text is empty"),
        (testdata, [], ["CODE", "CODE_TEXT"], RuntimeError, "text is empty"),
        (
            testdata,
            ["TASK", "PROBLEM"],
            ["CODETXT"],
            RuntimeError,
            "one or many context columns are not in data",
        ),
    ],
)
def test_create_text_with_content_raise_error(tdata, text, context, error, expected):
    """Test if inappropiate text or context columns, or data raise an exception."""
    with pytest.raises(error) as exception_info:
        TechnicalText(tdata, text, context)
    assert exception_info.match(expected)


def test_create_text_with_content(technical_text, expected_text, expected_context):
    """Test return value"""
    assert technical_text.text == expected_text
    assert technical_text.context == expected_context


def test_amend_characters_flags_regex_error(technical_text):
    """Test if inappropiate flags raise an regex exception."""
    with pytest.raises(re.error) as exception_info:
        technical_text.amend_characters(flags=1)
    assert exception_info.match("internal: unsupported template operator MAX_REPEAT")


def test_amend_characters_flags_type_error(technical_text):
    """Test if inappropiate flags raise a type exception."""
    with pytest.raises(TypeError) as exception_info:
        technical_text.amend_characters(flags="hello")
    assert exception_info.match("flags must be an 'RegexFlag' or 0")


def test_text_cleaning(technical_text):
    """Test return value of map_text_to_text, map_pattern_to_text, amend_characters"""
    actual = (
        technical_text.map_text_to_text({"c/o": "changeout"}, re.I)
        .map_pattern_to_text({"1pk-1234": "hydraulic ram"}, ID_PATTERN, re.I)
        .amend_characters({r"&": "and"}, re.I)
    )
    expected = [
        "changeout  seal in  hydraulic ram",
        "ladder cylinder rods corroded very bad causing damage to rod seals.",
        "no protective boots installed over cylinder rods allowing dust  and  dirt.",
    ]
    assert actual.text == expected


def test_map_pattern_to_text_unkn(technical_text):
    """Test return value"""
    actual = technical_text.map_pattern_to_text(
        {"1PK-1234": "hydraulic ram"}, ID_PATTERN, re.I
    )
    expected = [
        "c/o seal in  <UNKN>",
        "ladder cylinder rods corroded very bad causing damage to rod seals.",
        "no protective boots installed over cylinder rods allowing dust & dirt.",
    ]
    assert actual.text == expected
