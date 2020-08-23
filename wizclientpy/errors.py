from pathlib import Path
from datetime import datetime

from wizclientpy.constants import WIZNOTE_HOME

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


class WizException(Exception):
    """
    Generic WizNote exception.
    """
    logfile = str(Path(WIZNOTE_HOME).joinpath("log", "wizcli.log"))

    def exception_message_safe(self, exc):
        try:
            return str(exc)
        except Exception:
            return repr(exc)

    def logerror(self):
        """
        Logging exception to file.
        """
        iso_now = datetime.now().replace(microsecond=0).isoformat()
        msg = "{time}: [Error] {exc}\n".format(
            time=iso_now,
            exc=str(self)
        )
        with open(self.logfile, 'a') as log:
            log.write(msg)


class ServerXmlRpcError(WizException):
    """
    XML RPC error from Wiz server.

    You can pass server object to server argument.
    """
    def __init__(self, *args, **kwargs):
        self.server = kwargs.pop("server", None)
        super().__init__(*args, **kwargs)

    def server_message(self):
        if self.server:
            return " [Server: {}]".format(self.server.name)
        return ""

    def __str__(self):
        msg = super().__str__()
        if self.server:
            return "{}.{}".format(
                self.exception_message_safe(msg),
                self.server_message())


class InvalidUser(ServerXmlRpcError):
    def __init__(self, msg="User not exists!"):
        super().__init__(msg)


class InvalidPassword(ServerXmlRpcError):
    def __init__(self, msg="Password error!"):
        super().__init__(msg)


class InvalidToken(ServerXmlRpcError):
    def __init__(self, msg="User name or password is not correct!"):
        super().__init__(msg)


class TooManyLogins(ServerXmlRpcError):
    def __init__(self, msg="Log in too many times in a short time,"
                 "please try again later."):
        super().__init__(msg)


class PrivateError(Exception):
    def __init__(self, msg="This exception is raised when someone try to"
                 "access private attributes."):
        super().__init__(msg)


EXCEPTION_CODE_MAPPING = {
    InvalidToken: WIZKM_XMLRPC_ERROR_INVALID_TOKEN,
    InvalidUser: WIZKM_XMLRPC_ERROR_INVALID_USER,
    InvalidPassword: WIZKM_XMLRPC_ERROR_INVALID_PASSWORD,
    TooManyLogins: WIZKM_XMLRPC_ERROR_TOO_MANY_LOGINS,
}

CODE_EXCEPTION_MAPPING = dict([
    (301, InvalidToken),
    (31001, InvalidUser),
    (31002, InvalidPassword),
    (31004, TooManyLogins)
])
