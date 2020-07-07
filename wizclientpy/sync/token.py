import time

from wizclientpy.sync.kmserver import WizKMAccountsServer
from wizclientpy.errors import InvalidUser, InvalidPassword, TooManyLogins, ServerXmlRpcError
from wizclientpy.utils.classtools import MetaSingleton
from wizclientpy.constants import TOKEN_TIMEOUT_INTERVAL


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
            self.__info = as_server.user_info()
        # Check for token expiration
        if self.__info.tTokenExpried >= time.time():
            return self.__info.strToken
        else:
            # TODO: keep alive
            as_server = WizKMAccountsServer()
            as_server.set_user_info(self.__info)
            try:
                # Extend expiration time
                as_server.keep_alive()
                self.__info.tTokenExpried = time.time() + TOKEN_TIMEOUT_INTERVAL
                return self.__info.strToken
            except ServerXmlRpcError:
                # Get new token
                strToken = as_server.fetch_token(
                    self.__strUserId, self.__strPasswd)
                self.__info.strToken = strToken
                self.__info.tTokenExpried = time.time() + TOKEN_TIMEOUT_INTERVAL
                return strToken



