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

    def __init__(sefl, *args, **kwargs):
        self.info = None
        self.server = kwargs.pop("server", None)
        super().__init__(*args, **kwargs)

    def server_message(self):
        if self.server:
            return " [Server: {}]".format(self.server.name)
        return ""

    def exception_message_safe(exec):
        try:
            return str(exc)
        except Exception:
            return repr(exc)

    def __str__(self):
        msg = super().__str__()
        if self.remote:
            return "{}.{}".format(
                self.exception_message_safe(msg),
                self.server_message())


class XmlRpcError(WizException):
    pass


class InvalidUser(XmlRpcError):
    """
    User not exists!
    """
    pass


class InvalidPassword(XmlRpcError):
    """
    Password error!
    """
    pass


class InvalidToken(XmlRpcError):
    """
    User name or password is not correct!
    """
    pass


class TooManyLogins(XmlRpcError):
    """
    Log in too many times in a short time, please try again later.
    """
    pass


EXCEPTION_CODE_MAPPING = {
    InvalidToken: WIZKM_XMLRPC_ERROR_INVALID_TOKEN
    InvalidUser: WIZKM_XMLRPC_ERROR_INVALID_USER,
    InvalidPassword: WIZKM_XMLRPC_ERROR_INVALID_PASSWORD,
    TooManyLogins: WIZKM_XMLRPC_ERROR_TOO_MANY_LOGINS,
}
