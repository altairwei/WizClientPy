"""
WizNote API server.
"""
import requests

from wizclientpy.sync import api
from wizclientpy.sync.wizrequest import WizResp, json_request
from wizclientpy.sync.user_info import UserInfo, KbInfo, KbValueVersions
from wizclientpy.utils.classtools import MetaSingleton
from wizclientpy.utils.urltools import buildCommandUrl
from wizclientpy.constants import WIZKM_WEBAPI_VERSION


class WizKMApiServerBase:
    def __init__(self, strServer):
        while strServer.endswith("/"):
            strServer = strServer[:-1]
        if not strServer.startswith("http"):
            strServer = "https://" + strServer
        self.server = strServer

    def server(self):
        return self.server


class WizKMAccountsServer(WizKMApiServerBase, metaclass=MetaSingleton):
    """WizKMAccountsServer is used to manage account related information."""
    def __init__(self, strServer=api.newAsServerUrl()):
        self.isLogin = False
        self.autoLogout = False
        self.valueVersions = {}
        super().__init__(strServer)

    def login(self, user_name, password):
        """Login to server and get access token."""
        if self.isLogin:
            return True
        url = buildCommandUrl(self.server, "/as/user/login")
        result = json_request("POST", url, body={
            "userId": user_name,
            "password": password
        })
        # Update user information
        self.userInfo = UserInfo(result)
        self.isLogin = True
        return True

    def keep_alive(self):
        """Extended expiration time of token by 15 min."""
        if self.isLogin:
            url = buildCommandUrl(
                self.server, "/as/user/keep", self.userInfo.strToken)
            result = json_request("GET", url, token=self.userInfo.strToken)
            return result["maxAge"]
        else:
            raise ServerXmlRpcError("Can not keep alive without login.")

    def getToken(self, user_id, password):
        url = buildCommandUrl(self.server, "/as/user/token")
        result = json_request("POST", url, {
            "userId": user_id,
            "password": password
        })
        return result["token"]

    def setUserInfo(self, userInfo):
        self.isLogin = True
        self.userInfo = userInfo

    def getValueVersions(self):
        nCountPerPage = 100
        nNextVersion = 0
        url = buildCommandUrl(
            self.server, "/as/user/kv/versions", self.userInfo.strToken)
        result = json_request("GET", url, token=self.userInfo.strToken, body={
            'version': nNextVersion,
            'count': nCountPerPage,
            'pageSize': nCountPerPage
        })
        kbValVerCollection = []
        for obj in result:
            kbValVerCollection.append(KbValueVersions(obj))
        return kbValVerCollection

    def initAllValueVersions(self):
        versions = self.getValueVersions()
        for version in versions:
            self.valueVersions[version.strKbGUID] = version


class WizKMDatabaseServer(WizKMApiServerBase):
    """WizKMDatabaseServer is used to manage knowledge database."""
    def __init__(userInfo, kbInfo=KbInfo(), versions=KbValueVersions()):
        self.__userInfo = userInfo
        self.__kbInfo = kbInfo
        self.__valueVersions = versions

    def document_downloadDataNew(self):
        pass