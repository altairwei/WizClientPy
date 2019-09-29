"""
WizNote API server.
"""

from . import api

WIZKM_XMLRPC_ERROR_TRAFFIC_LIMIT = 304
WIZKM_XMLRPC_ERROR_STORAGE_LIMIT = 305
WIZKM_XMLRPC_ERROR_NOTE_COUNT_LIMIT = 3032
WIZKM_XMLRPC_ERROR_BIZ_SERVICE_EXPR = 380

WIZKM_XMLRPC_ERROR_FREE_SERVICE_EXPR = 30321
WIZKM_XMLRPC_ERROR_VIP_SERVICE_EXPR = 30322

# 返回的网络错误。 此处使用客户端自定义的错误代码
WIZKM_XMLRPC_ERROR_INVALID_TOKEN = 301
WIZKM_XMLRPC_ERROR_INVALID_USER = 31001
WIZKM_XMLRPC_ERROR_INVALID_PASSWORD = 31002
WIZKM_XMLRPC_ERROR_TOO_MANY_LOGINS = 31004

WIZKM_XMLRPC_ERROR_SYSTEM_ERROR = 60000

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
        self.login = False
        self.autoLogout = False
        super().__init__(api.newAsServerUrl())

    def login(self, user_name, password):
        if self.login:
            return True
        urlPath = "/as/user/login"
        url = self.buildUrl(urlPath)
        # TODO: Request token
        res = requests.post(url, json={
            "userId": user_name,
            "password": password
        })
        # TODO: handle error
        # TODO: Update user info

    def getToken(self):
        if not self.login:
            return ""
        return self.userInfo["strToken"]

    def buildUrl(self, urlPath):
        if urlPath.startswith("http://") or urlPath.startswith("https://"):
            url = urlPath
            return appendNormalParams(url, self.getToken())
        else:
            if not urlPath.startswith("/"):
                urlPath = "/" + urlPath
            url = getServer() + urlPath
            return appendNormalParams(url, self.getToken())
