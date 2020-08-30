import time

from wizclientpy.sync.api import ServerApi
from wizclientpy.sync.wizrequest import exec_request
from wizclientpy.sync.user_info import UserInfo
from wizclientpy.errors import (
    InvalidUser, InvalidPassword, InvalidToken,
    TooManyLogins, ServerXmlRpcError)
from wizclientpy.utils.classtools import MetaSingleton
from wizclientpy.constants import TOKEN_TIMEOUT_INTERVAL
from wizclientpy.utils.urltools import buildCommandUrl
from wizclientpy.utils.threadtools import IntervalTimer


class WizToken(ServerApi):
    """This class is used to manage the lifecycle of access token."""
    __timer: IntervalTimer
    __user_id: str
    __passwd: str
    __token: str

    def __init__(self, server, userId='', password=''):
        super().__init__(server)
        self.__user_id = userId
        self.__passwd = password
        self.__timer = IntervalTimer(
            TOKEN_TIMEOUT_INTERVAL, self.keep_alive)

    def set_identity(self, userId, password):
        self.__user_id = userId
        self.__passwd = password

    def __login(self):
        # Construct url
        url = self.build_url("/as/user/login")
        result = exec_request("POST", url, body={
            "userId": self.__user_id,
            "password": self.__passwd
        })
        return result

    def login(self) -> UserInfo:
        """Login to server and get an access token."""
        result = self.__login()
        # Update token
        user = UserInfo(self.server(), result)
        self.__token = user.token
        # Start keep alive timer
        self.__timer.start()
        return user

    def logout(self):
        """Cancel the current token."""
        try:
            url = self.build_url("/as/user/logout", self.__token)
            exec_request("GET", url, token=self.__token)
        finally:
            self.__timer.cancel()

    def keep_alive(self):
        """Make the current token alive."""
        try:
            url = self.build_url("/as/user/keep", self.__token)
            result = exec_request("GET", url, token=self.__token)
        except InvalidToken:
            # Get a new token
            result = self.__login()
            user = UserInfo(self.server(), result)
            self.__token = user.token

        return result

    def get(self):
        return self.__token
