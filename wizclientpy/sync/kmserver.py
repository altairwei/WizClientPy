"""
WizNote API server.
"""
from typing import Dict

import requests

from wizclientpy.sync.api import WIZNOTE_ACOUNT_SERVER
from wizclientpy.sync.wizrequest import exec_request
from wizclientpy.sync.user_info import UserInfo, KbInfo, KbValueVersions
from wizclientpy.sync.token import WizToken
from wizclientpy.utils.classtools import MetaSingleton
from wizclientpy.utils.urltools import buildCommandUrl
from wizclientpy.constants import WIZKM_WEBAPI_VERSION
from wizclientpy.errors import ServerXmlRpcError


class ServerApi:
    """Base class of api object."""
    __server: str

    def __init__(self, strServer: str):
        while strServer.endswith("/"):
            strServer = strServer[:-1]
        if not strServer.startswith("http"):
            strServer = "https://" + strServer
        self.__server = strServer

    def server(self):
        return self.__server


class AccountsServerApi(ServerApi):
    """AccountsServerApi is used to manage account related information."""
    __isLogin: bool
    __autoLogout: bool
    __valueVersions: Dict
    __userInfo: UserInfo

    def __init__(self, server: str = WIZNOTE_ACOUNT_SERVER):
        self.__isLogin = False
        self.__autoLogout = False
        self.__valueVersions = {}
        super().__init__(server)

    def login(self, user_name: str, password: str):
        """Login to server and get access token."""
        if self.__isLogin:
            return True
        url = buildCommandUrl(self.__server, "/as/user/login")
        result = exec_request("POST", url, body={
            "userId": user_name,
            "password": password
        })
        # Update user information
        self.__userInfo = UserInfo(result)
        self.__isLogin = True
        return result

    def logout(self) -> bool:
        """Logout the current token."""
        url = buildCommandUrl(
            self.__server, "/as/user/logout", self.__userInfo.strToken)
        result = exec_request("GET", url, token=self.__userInfo.strToken)
        return result

    def keep_alive(self):
        """Extended expiration time of token by 15 min."""
        if self.__isLogin:
            url = buildCommandUrl(
                self.__server, "/as/user/keep", self.__userInfo.strToken)
            result = exec_request("GET", url, token=self.__userInfo.strToken)
            return result
        else:
            raise ServerXmlRpcError("Can not keep alive without login.")

    def fetch_token(self, user_id, password):
        """Get a token by user identity."""
        url = buildCommandUrl(self.__server, "/as/user/token")
        result = exec_request("POST", url, {
            "userId": user_id,
            "password": password
        })
        return result

    def fetch_user_info(self):
        """Get user information from server by token."""
        url = buildCommandUrl(
            self.__server, "/as/user/keep", self.__userInfo.strToken)
        result = exec_request("GET", url, token=self.__userInfo.strToken)
        return result

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
            self.__server, "/as/user/kv/versions", self.__userInfo.strToken)
        result = exec_request(
            "GET", url, token=self.__userInfo.strToken, body={
                'version': nNextVersion,
                'count': nCountPerPage,
                'pageSize': nCountPerPage
            }
        )
        kbValVerCollection = []
        for obj in result:
            kbValVerCollection.append(KbValueVersions(obj))
        return kbValVerCollection

    def init_all_value_versions(self):
        versions = self.fetch_value_versions()
        for version in versions:
            self.__valueVersions[version.strKbGUID] = version


class KnowledgeBaseServerApi(ServerApi):
    """WizKMDatabaseServer is used to manage knowledge database."""
    __kbGuid: str
    __token: WizToken

    def __init__(self, server: str, kb_guid: str):
        self.__server = server
        self.__kbGuid = kb_guid

    def download_document(self, doc_guid: str):
        params = {
            "downloadInfo": True,
            "downloadData": True
        }
        url = buildCommandUrl(
            self.__server, f"/ks/note/download/{self.__kbGuid}/{doc_guid}",
            self.__userInfo.strToken)
        result = exec_request("GET", url, params=params)
        return result
