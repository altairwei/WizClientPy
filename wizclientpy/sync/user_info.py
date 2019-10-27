import time

from wizclientpy.constants import TOKEN_TIMEOUT_INTERVAL


class UserInfo:
    def __init__(self, info_json):
        self.strToken = info_json["token"]
        self.strKbGUID = info_json["kbGuid"]
        self.strKbServer = info_json["kbServer"]
        self.strMywizEmail = info_json["mywizEmail"]
        self.nUserLevel = info_json["userLevel"]
        self.strUserLevelName = info_json["userLevelName"]
        self.nUserPoints = info_json["userPoints"]
        self.strUserType = info_json["userType"]
        self.nMaxFileSize = info_json["uploadSizeLimit"]

        self.strInviteCode = info_json["inviteCode"]
        self.strNoticeText = info_json["noticeText"]
        self.strNoticeLink = info_json["noticeLink"]

        # TODO: use datetime object
        self.tVipExpried = info_json["vipDate"]

        user = info_json["user"]
        self.strUserEmail = user["email"]
        self.strDisplayName = user["displayName"]
        self.strUserGUID = user["userGuid"]
        self.tCreated = user["created"]
        # epoch time in seconds
        self.tTokenExpried = time.time() + TOKEN_TIMEOUT_INTERVAL

