import unittest
import tempfile
import os
from contextlib import contextmanager

from wizclientpy.database.user_setting import IniSetting


@contextmanager
def tempinput(data):
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(data)
    temp.close()
    try:
        yield temp.name
    finally:
        os.unlink(temp.name)


class IniConfigTestCase(unittest.TestCase):

    def test_getvalue(self):
        ini_file_content = b"""
        [DEFAULT]
        ServerAliveInterval = 45
        Compression = yes
        CompressionLevel = 9
        ForwardX11 = yes

        [bitbucket.org]
        User = hg

        [topsecret.server.com]
        Port = 50022
        ForwardX11 = no
        """
        with tempinput(ini_file_content) as ini_file:
            setting = IniSetting(ini_file)
            self.assertEqual(
                setting.value("DEFAULT/ServerAliveInterval"), "45")
            self.assertEqual(
                setting.value("DEFAULT/Compression"), "yes")
            self.assertEqual(
                setting.value("DEFAULT/CompressionLevel"), "9")
            self.assertEqual(
                setting.value("DEFAULT/ForwardX11"), "yes")
            self.assertEqual(
                setting.value("bitbucket.org/User"), "hg")
            self.assertEqual(
                setting.value("topsecret.server.com/Port"), "50022")
            self.assertEqual(
                setting.value("topsecret.server.com/ForwardX11"), "no")

    def test_setvalue(self):
        ini_file_content = b"""
        [DEFAULT]
        ServerAliveInterval = 45
        """
        with tempinput(ini_file_content) as ini_file:
            setting = IniSetting(ini_file)
            setting.set_value("DEFAULT/Compression", "yes")
            self.assertEqual(setting.value("DEFAULT/Compression"), "yes")
            setting.set_value("DEFAULT/CompressionLevel", "9")
            self.assertEqual(setting.value("DEFAULT/CompressionLevel"), "9")
            # New setion
            setting.set_value("bitbucket.org/User", "hg")
            self.assertEqual(setting.value("bitbucket.org/User"), "hg")
            setting.set_value("bitbucket.org/Location", "US")
            self.assertEqual(setting.value("bitbucket.org/Location"), "US")
            setting.set_value("topsecret.com/Port", "50022")
            self.assertEqual(setting.value("topsecret.com/Port"), "50022")

    def test_sync(self):
        ini_file_content = b"""
        """
        with tempinput(ini_file_content) as ini_file:
            setting = IniSetting(ini_file)
            setting.set_value("DEFAULT/Compression", "yes")
            setting.set_value("DEFAULT/CompressionLevel", "9")
            setting.set_value("bitbucket.org/User", "hg")
            setting.set_value("topsecret.com/Port", "50022")
            setting.sync()
            # New setting object
            setting2 = IniSetting(ini_file)
            self.assertEqual(setting2.value("DEFAULT/Compression"), "yes")
            self.assertEqual(setting2.value("DEFAULT/CompressionLevel"), "9")
            self.assertEqual(setting2.value("bitbucket.org/User"), "hg")
            self.assertEqual(setting2.value("topsecret.com/Port"), "50022")


if __name__ == '__main__':
    unittest.main()
