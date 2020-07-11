from typing import Dict
from limberframework.support.metaclasses import Singleton

class ConfigServiceProvider(metaclass=Singleton):
    def __init__(self, configs: Dict) -> None:
        self.configs = configs
