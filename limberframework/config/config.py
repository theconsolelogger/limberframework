"""Classes for accessing config settings."""
from ast import literal_eval
from configparser import ConfigParser
from typing import Dict


class Config(ConfigParser):
    """Wrapper class for ConfigParser.

    Provides helper functions for accessing options in
    the configuration files.
    """

    def get_section(self, section: str) -> Dict:
        """Retrieve a section from ConfigParser and casts the options.

        Args:
            section: Section to retrieve.

        Returns:
            dict: Cast options for the section.
        """
        section = self.__getitem__(section)
        options = {}

        for option, value in section.items():
            try:
                value = literal_eval(value)
            except (ValueError, SyntaxError):
                pass
            options[option] = value

        return options
