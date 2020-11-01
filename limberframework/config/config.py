from ast import literal_eval
from configparser import ConfigParser
from typing import Dict


class Config(ConfigParser):
    """Wrapper class for ConfigParser to provide
    helper functions for accessing options in
    the configuration files.
    """

    def get_section(self, section: str) -> Dict:
        """Retrieves a section from ConfigParser and
        casts the options.

        Arguments:
        section str -- section to retrieve

        Returns:
        dict -- cast options for the section
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
