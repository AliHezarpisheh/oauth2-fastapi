"""Module defining unit tests for the TomlParser class."""

from unittest.mock import mock_open, patch

import pytest

from toolkit.parsers import TomlParser
from toolkit.parsers.helpers.exceptions import TomlParsingError

SAMPLE_TOML_CONTENT = """
[info]
name = "John"
age = 30
"""

FILE_PATH = "test.toml"


@pytest.fixture
def toml_parser() -> TomlParser:
    """Fixture to instantiate TomlParser."""
    return TomlParser(file_path=FILE_PATH)


@pytest.mark.smoke
def test_read(toml_parser: TomlParser) -> None:
    """Verify reading a valid TOML file."""
    # Arrange & Act
    with patch("pathlib.Path.open", mock_open(read_data=SAMPLE_TOML_CONTENT)):
        content = toml_parser.read()

    # Assert
    assert content == {"info": {"name": "John", "age": 30}}


def test_read_invalid_syntax_toml_file(
    toml_parser: TomlParser,
) -> None:
    """Verify reading an invalid TOML file."""
    # Arrange & Act & Assert
    with patch("pathlib.Path.open", mock_open(read_data="invalid syntax")):
        with pytest.raises(TomlParsingError, match=r"Syntax Error in: `test.toml`!"):
            toml_parser.read()
