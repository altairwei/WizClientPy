"""
WizNote API server.
"""
import requests

from wizclientpy.sync import api
from wizclientpy.sync.wizresp import WizResp
from wizclientpy.sync.user_info import UserInfo
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

    def getServer(self):
        return self.server


class WizKMAccountsServer(WizKMApiServerBase, metaclass=MetaSingleton):
    def __init__(self, strServer=api.newAsServerUrl()):
        self.isLogin = False
        self.autoLogout = False
        super().__init__(strServer)

    def login(self, user_name, password):
        if self.isLogin:
            return True
        url = buildCommandUrl(self.server, "/as/user/login")
        res = requests.post(url, json={
            "userId": user_name,
            "password": password
        })
        res_json = WizResp(res).json()
        # Update user information
        self.userInfo = UserInfo(res_json["result"])
        self.isLogin = True
        return True

    def keepAlive(self):
        """Extended expiration time of token by 15 min."""
        if self.isLogin:
            url = buildCommandUrl(
                self.server, "/as/user/keep", self.userInfo.strToken)
            res = requests.get(url)
            res_json = WizResp(res).json()
            return res_json["result"]["maxAge"]
        else:
            raise ServerXmlRpcError("Can not keep alive without login.")

    def getToken(self, user_id, password):
        url = buildCommandUrl(self.server, "/as/user/token")
        res = requests.post(url, json={
            "userId": user_id,
            "password": password
        })
        result = WizResp(res).result()
        return result["token"]

    def setUserInfo(self, userInfo):
        self.isLogin = True
        self.userInfo = userInfo
