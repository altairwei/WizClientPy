import unittest
import os
import tempfile
import sqlite3

from wizclientpy.constants import WIZNOTE_HOME
from wizclientpy.database.user_setting import DatabaseSetting, UserSetting


class DatabaseSettingTestCase(unittest.TestCase):
    def setUp(self):
        temp = tempfile.NamedTemporaryFile(delete=False)
        temp.close()
        self.__db_filename = temp.name
        with sqlite3.connect(self.__db_filename) as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE WIZ_META
                (
                    META_NAME                       varchar(50),
                    META_KEY                        varchar(50),
                    META_VALUE                      varchar(3000),
                    DT_MODIFIED                     char(19),
                    primary key (META_NAME, META_KEY)
                );
            """)
            records = [
                ('ACCOUNT', 'DISPLAYNAME', 'test_api', '2020-08-22 20:45:55'),
                ('ACCOUNT', 'USERLEVEL', '1', '2020-08-22 20:45:55'),
                ('ACCOUNT', 'KBSERVER', 'api.wiz.cn', '2020-08-22 20:45:55'),
                ('ACCOUNT', 'USERID', 'test_api@wiz.cn', '2020-08-22 20:45:55'),
                ('ACCOUNT', 'PASSWORD', None, '2020-08-22 20:45:55'),
                ('QT_WIZNOTE', 'AUTOLOGIN', '0', '2020-08-22 20:45:55'),
                ('TABLESTRUCTURE', 'VERSION', '5', '2020-08-22 20:45:55')
            ]
            c.executemany('insert into WIZ_META VALUES(?,?,?,?);', records)

    def tearDown(self):
        os.remove(self.__db_filename)

    def test_getvalue(self):
        setting = DatabaseSetting(self.__db_filename)
        self.assertEqual(setting.value("ACCOUNT/USERID"), "test_api@wiz.cn")
        self.assertEqual(setting.value("ACCOUNT/KBSERVER"), "api.wiz.cn")
        self.assertEqual(setting.value("ACCOUNT/USERLEVEL"), "1")
        self.assertEqual(setting.value("QT_WIZNOTE/AUTOLOGIN"), "0")
        self.assertEqual(setting.value("TABLESTRUCTURE/VERSION"), "5")

    def test_default(self):
        setting = DatabaseSetting(self.__db_filename)
        self.assertEqual(
            setting.value("ACCOUNT/USERID", "hello"), "test_api@wiz.cn")
        self.assertEqual(setting.value("QT_WIZNOTE/AUTOLOGIN", "7"), "0")
        self.assertEqual(setting.value("ACCOUNT/HELLO", "world"), "world")
        self.assertEqual(setting.value("LOCATION/HELLO", "world"), "world")

    def test_setvalue(self):
        setting = DatabaseSetting(self.__db_filename)
        # Update exist records
        setting.set_value("ACCOUNT/USERID", "test@wiz.cn")
        self.assertEqual(setting.value("ACCOUNT/USERID"), "test@wiz.cn")
        setting.set_value("ACCOUNT/USERLEVEL", "7")
        self.assertEqual(setting.value("ACCOUNT/USERLEVEL"), "7")
        # Insert new record
        setting.set_value("SYNC_INFO/DELETED_GUID", "15")
        self.assertEqual(setting.value("SYNC_INFO/DELETED_GUID"), "15")
        setting.set_value("GROUPS/COUNT", "2")
        self.assertEqual(setting.value("GROUPS/COUNT"), "2")
        # Null value
        setting.set_value("ACCOUNT/PASSWORD", "helloworld")
        self.assertEqual(setting.value("ACCOUNT/PASSWORD"), "helloworld")


__test_index_db = os.path.join(
    WIZNOTE_HOME, "test_api@wiz.cn", "data", "index.db")

@unittest.skipUnless(
    os.path.exists(__test_index_db), "WizNote test account not found.")
class UserSettingTestCase(unittest.TestCase):
    def test_getvalue(self):
        setting = UserSetting("test_api@wiz.cn")
        self.assertEqual(setting.value("ACCOUNT/USERID"), "test_api@wiz.cn")
        self.assertEqual(setting.value("ACCOUNT/DISPLAYNAME"), "test_api")
        self.assertEqual(setting.value("DATABASE/KBGUID"),
                         "d9916970-4c7d-11ea-8dde-0dc922a157b9")

    def test_default(self):
        setting = UserSetting("test_api@wiz.cn")
        self.assertEqual(setting.value("ACCOUNT/USER", "hello"), "hello")
        self.assertEqual(setting.value("WORLD/USER", "world"), "world")


if __name__ == '__main__':
    unittest.main()
