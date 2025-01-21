import pytest
import base64

from tusfastapiserver.utils.metadata import (
    validate_key,
    validate_value,
    parse,
    stringify,
)
from tusfastapiserver.exceptions import InvalidMetadataException


@pytest.mark.parametrize(
    "key, expected",
    [
        ("", False),  # Empty key -> False
        ("validKey", True),  # Simple valid ASCII key -> True
        ("key_with_underscores", True),
        ("key with space", False),  # Contains space -> False
        ("key,with,comma", False),  # Contains comma -> False
        ("kéy", False),  # Non-ASCII -> False
    ],
)
def test_validate_key(key, expected):
    assert validate_key(key) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (None, False),  # None -> False
        ("dGVzdA", False),  # Length not multiple of 4
        ("@@@@", False),  # Does not match BASE64_REGEX
        ("dGVzdA==", True),  # "test" in Base64 -> True
        ("cHl0aG9u", True),  # "python" in Base64 (no padding) -> True
    ],
)
def test_validate_value(value, expected):
    assert validate_value(value) == expected


def test_parse_none():
    """parse(None) -> None."""
    assert parse(None) is None


def test_parse_empty_string():
    """parse('') -> None."""
    assert parse("") is None


def test_parse_whitespace_only():
    """parse('   ') -> raises InvalidMetadataException."""
    with pytest.raises(InvalidMetadataException):
        parse("   ")


def test_parse_single_valid_pair():
    """parse('foo dGVzdA==') -> {'foo': 'test'}."""
    result = parse("foo dGVzdA==")
    assert result == {"foo": "test"}


def test_parse_single_key_without_value():
    """parse('foo') -> {'foo': None}."""
    result = parse("foo")
    assert result == {"foo": None}


def test_parse_multiple_pairs():
    """parse('foo dGVzdA==,bar cHl0aG9u') -> {'foo': 'test', 'bar': 'python'}."""
    result = parse("foo dGVzdA==,bar cHl0aG9u")
    assert result == {"foo": "test", "bar": "python"}


def test_parse_invalid_key():
    """Key contains space -> raise InvalidMetadataException."""
    with pytest.raises(InvalidMetadataException):
        parse("foo dGVzdA==,bad key dGVzdA==")


def test_parse_invalid_value():
    """Value not multiple of 4 -> raise InvalidMetadataException."""
    with pytest.raises(InvalidMetadataException):
        parse("foo bad_base64,bar cHl0aG9u")


def test_parse_repeated_key():
    """Same key repeated -> raise InvalidMetadataException."""
    with pytest.raises(InvalidMetadataException):
        parse("foo dGVzdA==,foo cHl0aG9u")


def test_stringify_single_pair():
    """stringify({'foo': 'test'}) -> 'foo dGVzdA=='."""
    meta = {"foo": "test"}
    result = stringify(meta)
    assert result == "foo dGVzdA=="


def test_stringify_single_none_value():
    """stringify({'foo': None}) -> 'foo'."""
    meta = {"foo": None}
    result = stringify(meta)
    assert result == "foo"


def test_stringify_multiple_pairs():
    """
    stringify({'foo': 'test', 'bar': 'python'})
    -> 'foo dGVzdA==,bar cHl0aG9u'
    (or possibly 'bar cHl0aG9u,foo dGVzdA==' if dict order differs in your Python version).
    """
    meta = {"foo": "test", "bar": "python"}
    result = stringify(meta).split(",")
    assert sorted(result) == sorted(["foo dGVzdA==", "bar cHl0aG9u"])


def test_stringify_encoding_check():
    """Ensure the correct Base64 encoding is produced."""
    meta = {"hello": "world"}
    encoded_world = base64.b64encode(b"world").decode("utf-8")
    result = stringify(meta)
    assert result == f"hello {encoded_world}"
