from pytest import fixture
from limberframework.config.config import Config


@fixture
def config():
    return Config()


def test_init(config):
    assert config.config == {}


def test_get_item(config):
    config.config["test"] = True

    assert config["test"]


def test_set_item(config):
    config["test"] = True

    assert config.config == {"test": True}
