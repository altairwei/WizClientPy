"""
WizNote API server.
"""
import requests

from wizclientpy.sync import api
from wizclientpy.sync.wizresp import WizResp
from wizclientpy.sync.user_info import UserInfo
from wizclientpy.utils.classtools import MetaSingleton
from wizclientpy.constants import WIZKM_WEBAPI_VERSION


def appendNormalParams(strUrl, token):
    if "?" not in strUrl:
        strUrl += "?"
    else:
        strUrl += "&"
    strUrl += (
        "clientType=macos"  # macos means WizQTClient
        "&clientVersion={client_version}"
        "&apiVersion={api_version}"
    ).format(
        client_version=None,
        api_version=WIZKM_WEBAPI_VERSION
    )
    if token:
        strUrl += "&token=" + token
    strUrl = api.appendSrc(strUrl)
    return strUrl


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
        url = self.buildUrl("/as/user/login")
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
        url = self.buildUrl("/as/user/keep")
        res = requests.get(url)
        res_json = WizResp(res).json()
        pass

    def getToken(self):
        if not self.isLogin:
            return ""
        return self.strToken

    def buildUrl(self, urlPath):
        if urlPath.startswith("http://") or urlPath.startswith("https://"):
            url = urlPath
            return appendNormalParams(url, self.getToken())
        else:
            if not urlPath.startswith("/"):
                urlPath = "/" + urlPath
            url = self.getServer() + urlPath
            return appendNormalParams(url, self.getToken())
