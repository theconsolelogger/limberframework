from configparser import ConfigParser
from unittest.mock import Mock

from limberframework.config.config import Config


def test_init():
    config = Config()
    assert isinstance(config, Config)
    assert isinstance(config, ConfigParser)


def test_get_section():
    config = Config()
    config.__getitem__ = Mock(
        return_value={"db": "0", "host": "http://localhost", "port": "1234"}
    )

    section = config.get_section("test")

    assert section == {"db": 0, "host": "http://localhost", "port": 1234}
