import os
import configparser

from wizclientpy.constants import WIZNOTE_HOME_DIR
from wizclientpy.utils.classtools import MetaSingleton
from wizclientpy.errors import WizException


class IniSetting:
    __config_file: str
    __config: configparser.ConfigParser

    def __init__(self, config_file):
        self.__config_file = config_file
        self.__config = configparser.ConfigParser()
        self.__config.read(self.__config_file)

    def value(self, key: str, default=None):
        key_parts = key.split("/")
        try:
            p = self.__config
            for part in key_parts:
                p = p[part]
            return p
        except (configparser.NoOptionError,
                configparser.NoOptionError, KeyError):
            return default

    def set_value(self, key: str, value):
        key_parts = key.split("/")
        if len(key_parts) > 2:
            raise WizException("too many keys")
        try:
            self.__config[key_parts[0]][key_parts[1]] = value
        except (configparser.NoOptionError,
                configparser.NoOptionError, KeyError):
            self.__config[key_parts[0]] = {}
            self.__config[key_parts[0]][key_parts[1]] = value

    def sync(self):
        with open(self.__config_file, 'w') as f:
            self.__config.write(f)


class GlobalSetting(IniSetting, metaclass=MetaSingleton):

    def __init__(self):
        super().__init__(os.path.join(WIZNOTE_HOME_DIR, "wiznote.ini"))
