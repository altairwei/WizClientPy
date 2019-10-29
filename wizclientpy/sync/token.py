import time

from wizclientpy.sync.kmserver import WizKMAccountsServer
from wizclientpy.errors import InvalidUser, InvalidPassword, TooManyLogins
from wizclientpy.utils.classtools import MetaSingleton


class WizToken(metaclass=MetaSingleton):
    """This singleton is used to manage the lifecycle of access token."""

    def __init__(self, userId='', password=''):
        self.__strUserId = userId
        self.__strPasswd = password
        self.__info = None

    def setUserId(self, userId):
        self.__strUserId = userId

    def setPasswd(self, password):
        self.__strPasswd = password

    def userInfo(self):
        return self.__info

    def token(self):
        # Login to server
        if not self.__info:
            as_server = WizKMAccountsServer()
            as_server.login(self.__strUserId, self.__strPasswd)
            self.__info = as_server.userInfo
        # Check for token expiration
        if self.__info.tTokenExpried >= time.time():
            return self.__info.strToken
        else:
            # TODO: keep alive
            pass



