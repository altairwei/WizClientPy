"""This module provides some useful tools for handling URL."""

from urllib.parse import urlparse

from wizclientpy.constants import WIZKM_WEBAPI_VERSION


def appendSrc(url):
    url += "&srcHost=%s" % urlparse(url).netloc
    return url


def buildCommandUrl(server, cmdUrl, strToken):
    # Construct url
    if cmdUrl.startswith("http://") or cmdUrl.startswith("https://"):
        strUrl = cmdUrl
    else:
        if not cmdUrl.startswith("/"):
            cmdUrl = "/" + cmdUrl
        strUrl = server + cmdUrl
    # Append common parameters
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
    if strToken:
        strUrl += "&token=" + strToken
    strUrl = appendSrc(strUrl)
    return strUrl
