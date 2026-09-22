"""Tests for the output-language directive helper."""

from server.utils.language import (
    DEFAULT_OUTPUT_LANGUAGE,
    VALID_OUTPUT_LANGUAGES,
    language_directive,
    normalize_output_language,
)


def test_auto_returns_empty_directive():
    # 'auto' must not add any instruction so the model matches the input.
    assert language_directive("auto") == ""


def test_default_language_is_auto():
    assert DEFAULT_OUTPUT_LANGUAGE == "auto"
    assert language_directive(DEFAULT_OUTPUT_LANGUAGE) == ""


def test_english_directive_mentions_english():
    directive = language_directive("english")
    assert directive
    assert "English" in directive


def test_arabic_directive_mentions_arabic():
    directive = language_directive("arabic")
    assert directive
    assert "Arabic" in directive


def test_bilingual_directive_mentions_both():
    directive = language_directive("bilingual")
    assert "English" in directive
    assert "Arabic" in directive


def test_unknown_and_empty_values_fall_back_to_auto():
    for value in (None, "", "  ", "fr", "klingon", 123, {}):
        assert language_directive(value) == ""
        assert normalize_output_language(value) == "auto"


def test_normalize_is_case_and_whitespace_insensitive():
    assert normalize_output_language("  Arabic ") == "arabic"
    assert normalize_output_language("ENGLISH") == "english"


def test_all_valid_languages_normalize_to_themselves():
    for value in VALID_OUTPUT_LANGUAGES:
        assert normalize_output_language(value) == value
