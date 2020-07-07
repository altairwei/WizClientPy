"""
WizNote API server.
"""
from typing import Dict

import requests

from wizclientpy.sync import api
from wizclientpy.sync.wizrequest import WizResp, json_request
from wizclientpy.sync.user_info import UserInfo, KbInfo, KbValueVersions
from wizclientpy.utils.classtools import MetaSingleton
from wizclientpy.utils.urltools import buildCommandUrl
from wizclientpy.constants import WIZKM_WEBAPI_VERSION


class WizKMApiServerBase:
    """Base class of api object."""
    server: str

    def __init__(self, strServer: str):
        while strServer.endswith("/"):
            strServer = strServer[:-1]
        if not strServer.startswith("http"):
            strServer = "https://" + strServer
        self.server = strServer

    def server(self):
        return self.server


class WizKMAccountsServer(WizKMApiServerBase, metaclass=MetaSingleton):
    """WizKMAccountsServer is used to manage account related information."""
    __isLogin: bool
    __autoLogout: bool
    __valueVersions: Dict
    __userInfo: UserInfo

    def __init__(self, strServer: str = api.newAsServerUrl()):
        self.__isLogin = False
        self.__autoLogout = False
        self.__valueVersions = {}
        super().__init__(strServer)

    def login(self, user_name: str, password: str) -> bool:
        """Login to server and get access token."""
        if self.__isLogin:
            return True
        url = buildCommandUrl(self.server, "/as/user/login")
        result = json_request("POST", url, body={
            "userId": user_name,
            "password": password
        })
        # Update user information
        self.__userInfo = UserInfo(result)
        self.__isLogin = True
        return True

    def logout(self) -> bool:
        """Logout the current token."""
        url = buildCommandUrl(
            self.server, "/as/user/logout", self.__userInfo.strToken)
        json_request("GET", url, token=self.__userInfo.strToken)
        return True

    def keep_alive(self):
        """Extended expiration time of token by 15 min."""
        if self.__isLogin:
            url = buildCommandUrl(
                self.server, "/as/user/keep", self.__userInfo.strToken)
            result = json_request("GET", url, token=self.__userInfo.strToken)
            return result["maxAge"]
        else:
            raise ServerXmlRpcError("Can not keep alive without login.")

    def fetch_token(self, user_id, password):
        """Get a token by user identity."""
        url = buildCommandUrl(self.server, "/as/user/token")
        result = json_request("POST", url, {
            "userId": user_id,
            "password": password
        })
        return result["token"]

    def fetch_user_info(self) -> UserInfo:
        """Get user information from server by token."""
        url = buildCommandUrl(
            self.server, "/as/user/keep", self.__userInfo.strToken)
        result = json_request("GET", url, token=self.__userInfo.strToken)

    def user_info(self) -> UserInfo:
        """Access to user information object."""
        return self.__userInfo

    def set_user_info(self, userInfo: UserInfo):
        """Set new user info."""
        self.__isLogin = True
        self.__userInfo = userInfo

    def fetch_value_versions(self):
        nCountPerPage = 100
        nNextVersion = 0
        url = buildCommandUrl(
            self.server, "/as/user/kv/versions", self.__userInfo.strToken)
        result = json_request("GET", url, token=self.__userInfo.strToken, body={
            'version': nNextVersion,
            'count': nCountPerPage,
            'pageSize': nCountPerPage
        })
        kbValVerCollection = []
        for obj in result:
            kbValVerCollection.append(KbValueVersions(obj))
        return kbValVerCollection

    def init_all_value_versions(self):
        versions = self.fetch_value_versions()
        for version in versions:
            self.__valueVersions[version.strKbGUID] = version


class WizKMDatabaseServer(WizKMApiServerBase):
    """WizKMDatabaseServer is used to manage knowledge database."""
    def __init__(userInfo, kbInfo=KbInfo(), versions=KbValueVersions()):
        self.__userInfo = userInfo
        self.__kbInfo = kbInfo
        self.__valueVersions = versions

    def document_downloadDataNew(self):
        pass