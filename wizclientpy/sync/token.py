
from wizclientpy.sync.kmserver import WizKMAccountsServer
from wizclientpy.errors import InvalidUser, InvalidPassword, TooManyLogins
from wizclientpy.utils.classtools import MetaSingleton


class WizToken(metaclass=MetaSingleton):
    """This singleton is used to manage the lifecycle of access token."""

    def __init__(self, userId='', password=''):
        self.__info = None
        self.__strUserId = userId
        self.__strPasswd = password
        self.__strToken = ''

    def setUserId(self, userId):
        self.__strUserId = userId

    def setPasswd(self, password):
        self.__strPasswd = password

    def userInfo(self):
        return self.__info

    def token(self):
        as_server = WizKMAccountsServer()
        as_server.login(self.__strUserId, self.__strPasswd)
        self.__info = as_server.userInfo
        # Set `self.__info` tTokenExpried if not
        return self.__info.strToken



