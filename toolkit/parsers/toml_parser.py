"""Contains the TomlParser class for parsing Toml files."""

from typing import Any

import tomlkit

from .abc import Parser
from .helpers.exceptions import TomlParsingError


class TomlParser(Parser):
    """Parses Toml files and loads their content."""

    def read(self) -> Any:
        """
        Read a Toml file and return its content as a dictionary.

        Returns
        -------
        Any
            The parsed content of the Toml file.
        """
        try:
            with self.file_path.open(mode="rb") as file:
                content = tomlkit.load(file)
        except tomlkit.exceptions.ParseError as err:
            msg = f"Syntax Error in: `{self.file_path}`!"
            print(msg)
            raise TomlParsingError(msg) from err
        else:
            return content
