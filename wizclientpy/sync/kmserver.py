"""
WizNote API server.
"""
import requests
from . import api

WIZKM_WEBAPI_VERSION = 10


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


class WizKMApiServerBase(object):
    def __init__(self, strServer):
        while strServer.endswith("/"):
            strServer = strServer[:-1]
        self.server = strServer

    def getServer(self):
        return self.server


class WizKMAccountsServer(WizKMApiServerBase):
    def __init__(self):
        self.isLogin = False
        self.autoLogout = False
        super().__init__(api.newAsServerUrl())

    def login(self, user_name, password):
        if self.isLogin:
            return True
        urlPath = "/as/user/login"
        url = self.buildUrl(urlPath)
        # TODO: Request token
        res = requests.post(url, json={
            "userId": user_name,
            "password": password
        })
        # TODO: handle error
        res_json = res.json()
        # TODO: Update user info
        self.userInfo = res_json["result"]
        return True

    def getToken(self):
        if not self.isLogin:
            return ""
        return self.userInfo["strToken"]

    def buildUrl(self, urlPath):
        if urlPath.startswith("http://") or urlPath.startswith("https://"):
            url = urlPath
            return appendNormalParams(url, self.getToken())
        else:
            if not urlPath.startswith("/"):
                urlPath = "/" + urlPath
            url = self.getServer() + urlPath
            return appendNormalParams(url, self.getToken())
