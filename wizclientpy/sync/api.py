"""
This module is used as a tools to build WizNote APIs.
"""

import json
import platform
import random
import time
import locale
import requests
from urllib.parse import urlparse

from wizclientpy.utils.urltools import appendSrc

WIZNOTE_API_ENTRY = (
    "{server}"  # address of WizNote server
    "?p={product}"  # product, use wiz
    "&l={locale}"  # locale, zh-cn|zh-tw|en-us
    "&v={version}"  # version number
    "&c={command}"  # command, see command list below
    "&random={ramdom}"  # ramdom number
    "&cn={computer_name}"  # computer name, optional
    "&plat={platform}"  # platform, ios|android|web|wp7|x86|x64|linux|macosx
    "&debug={debug}"  # debug, true|false, optional
)

WIZNOTE_API_ARG_PRODUCT = "wiz"

if platform.system() == "Windows":
    WIZNOTE_API_ARG_PLATFORM = "windows"
elif platform.system() == "Darwin":
    WIZNOTE_API_ARG_PLATFORM = "macosx"
elif platform.system() == "Linux":
    WIZNOTE_API_ARG_PLATFORM = "linux"

# API commands
WIZNOTE_API_COMMAND_AS_SERVER = "as"
WIZNOTE_API_COMMAND_SYNC_HTTP = "sync_http"
WIZNOTE_API_COMMAND_SYNC_HTTPS = "sync_https"
WIZNOTE_API_COMMAND_MESSAGE_SERVER = "message_server"
WIZNOTE_API_COMMAND_MESSAGE_VERSION = "message_version"
WIZNOTE_API_COMMAND_AVATAR = "avatar"
WIZNOTE_API_COMMAND_UPLOAD_AVATAR = "upload_avatar"
WIZNOTE_API_COMMAND_USER_INFO = "user_info"
WIZNOTE_API_COMMAND_VIEW_GROUP = "view_group"
WIZNOTE_API_COMMAND_FEEDBACK = "feedback"
WIZNOTE_API_COMMAND_SUPPORT = "support"
WIZNOTE_API_COMMAND_COMMENT = "comment"
WIZNOTE_API_COMMAND_COMMENT_COUNT = "comment_count2"
WIZNOTE_API_COMMAND_CHANGELOG = "changelog"
WIZNOTE_API_COMMAND_UPGRADE = "updatev2"
WIZNOTE_API_COMMAND_MAIL_SHARE = "mail_share2"

WIZNOTE_API_SERVER = "https://api.wiz.cn/"

_server = WIZNOTE_API_SERVER
_url_cache = dict()


def setEnterpriseServerIP(strIP):
    if strIP and strIP == _server:
        return
    if strIP:
        if strIP.startswith("http"):
            _server = strIP
            if not _server.endswith("/"):
                _server += "/"
        else:
            _server = "http://%s/" % strIP
    else:
        raise Exception("can not set a empty server address")


def makeUpUrlFromCommand(strCommand):
    """
    Create API command query url.
    """
    random.seed(int(round(time.time() * 1000)))
    lang = locale.getdefaultlocale()
    strUrl = WIZNOTE_API_ENTRY.format(
        server=_server,
        product=WIZNOTE_API_ARG_PRODUCT,
        locale=lang[0].replace("_", "-").lower(),
        version="",
        command=strCommand,
        ramdom=random.randrange(100000),
        computer_name="",
        platform=WIZNOTE_API_ARG_PLATFORM,
        debug="false"
    )
    strUrl = appendSrc(strUrl)
    return strUrl


def ensure_success(res):
    if not res.status_code == requests.codes.ok:
        raise Exception(res)
    # TODO: handle incorrect return code.


def json_from_response(res):
    ensure_success(res)
    return res.json()


def requestUrl(strCommand):
    url = makeUpUrlFromCommand(strCommand)
    res = requests.get(url)
    ensure_success(res)
    return res.text


def getEndPoints():
    """
    Get API commands and corresponding urls.
    """
    url = makeUpUrlFromCommand("endpoints")
    res = requests.get(url)
    res_json = json_from_response(res)
    _url_cache.update(res_json)


def getUrlFromCache(strCommand):
    if not _url_cache:
        getEndPoints()
    try:
        return _url_cache[strCommand]
    except KeyError:
        return ""


def getUrlByCommand(strCommand):
    """
    Query API url by API command.
    """
    strUrl = getUrlFromCache(strCommand)
    if not strUrl:
        strUrl = requestUrl(strCommand)
        if strUrl and strUrl.startswith("http"):
            _url_cache[strCommand] = strUrl
    return strUrl


def newAsServerUrl():
    key = "account_server_url"
    strAsUrl = getUrlByCommand(key)
    if not strAsUrl.startswith("http"):
        strAsUrl = "https://as.wiz.cn"
    return strAsUrl
