import os
import configparser
import sqlite3
from datetime import datetime

from wizclientpy.constants import WIZNOTE_HOME
from wizclientpy.utils.classtools import MetaSingleton
from wizclientpy.errors import WizException


class SettingKeyError(WizException):
    def __init__(self, msg="key must have to parts, split with '/'"):
        super().__init__(msg)


class BaseKeySetting:
    def split_key(self, key):
        key_parts = key.split("/")
        if len(key_parts) != 2:
            raise SettingKeyError
        if not key_parts[0] or not key_parts[1]:
            raise SettingKeyError("key is empty")
        return key_parts


class IniSetting(BaseKeySetting):
    __config_file: str
    __config: configparser.ConfigParser

    def __init__(self, config_file):
        self.__config_file = config_file
        self.__config = configparser.ConfigParser()
        self.__config.read(self.__config_file)

    def value(self, key: str, default=None):
        key_parts = self.split_key(key)
        try:
            p = self.__config
            for part in key_parts:
                p = p[part]
            return p
        except (configparser.NoOptionError,
                configparser.NoOptionError, KeyError):
            return default

    def set_value(self, key: str, value):
        key_parts = self.split_key(key)
        try:
            self.__config[key_parts[0]][key_parts[1]] = value
        except (configparser.NoOptionError,
                configparser.NoOptionError, KeyError):
            self.__config[key_parts[0]] = {}
            self.__config[key_parts[0]][key_parts[1]] = value

    def sync(self):
        """Writes any unsaved changes to ini file."""
        with open(self.__config_file, 'w') as f:
            self.__config.write(f)


class GlobalSetting(IniSetting, metaclass=MetaSingleton):

    def __init__(self):
        super().__init__(os.path.join(WIZNOTE_HOME, "wiznote.ini"))


class DatabaseSetting(BaseKeySetting):
    __db_file: str

    def __init__(self, db_file: str):
        self.__db_file = db_file

    def value(self, key, default=None):
        key_parts = self.split_key(key)
        meta_name = key_parts[0].upper()
        meta_key = key_parts[1].upper()
        # FIXME: move sql to WizDatabase
        with sqlite3.connect(self.__db_file) as index_db:
            cursor = index_db.cursor()
            sql_cmd = "select META_VALUE from WIZ_META"
            sql_cmd += " where META_NAME='%s'" % meta_name
            sql_cmd += " and META_KEY='%s'" % meta_key
            cursor.execute(sql_cmd)
            row = cursor.fetchone()
            if row:
                return row[0]
            else:
                return default

    def set_value(self, key, value):
        key_parts = self.split_key(key)
        meta_name = key_parts[0].upper()
        meta_key = key_parts[1].upper()
        old_value = self.value(key)
        if old_value == value:
            return
        # FIXME: move sql to WizDatabase
        with sqlite3.connect(self.__db_file) as index_db:
            cursor = index_db.cursor()
            if old_value:
                # update
                sql_cmd = """
                update WIZ_META set META_VALUE='{value}', DT_MODIFIED='{time}'
                where META_NAME='{name}' and META_KEY='{key}'
                """.format(
                    value=value,
                    name=meta_name,
                    key=meta_key,
                    time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
            else:
                # Insert
                sql_cmd = """
                insert into WIZ_META (
                    META_NAME, META_KEY, META_VALUE, DT_MODIFIED)
                values ('{name}', '{key}', '{value}', '{time}')
                """.format(
                    name=meta_name,
                    key=meta_key,
                    value=value,
                    time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
            cursor.execute(sql_cmd)


class UserSetting(DatabaseSetting):
    __user_id: str

    def __init__(self, user_id: str):
        self.__user_id = user_id
        super().__init__(os.path.join(
            WIZNOTE_HOME, user_id, "data", "index.db"))
