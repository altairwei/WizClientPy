import time

from wizclientpy.constants import TOKEN_TIMEOUT_INTERVAL


class UserInfo:
    """Represents user information."""
    def __init__(self, info_json):
        self.fromJson(info_json)

    def fromJson(self, info_json):
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

        self.tVipExpried = info_json["vipDate"]

        user = info_json["user"]
        self.strUserEmail = user["email"]
        self.strDisplayName = user["displayName"]
        self.strUserGUID = user["userGuid"]
        self.tCreated = user["created"]
        # epoch time in seconds
        self.tTokenExpried = time.time() + TOKEN_TIMEOUT_INTERVAL

    def __str__(self):
        out = "[User '%s']\n" % self.strDisplayName
        for key in self.__dict__:
            if key in ["tCreated", "tVipExpried"]:
                value = time.asctime(time.localtime(self.__dict__[key]/1000))
            elif key == "tTokenExpried":
                value = time.asctime(time.localtime(self.__dict__[key]))
            else:
                value = self.__dict__[key]
            out += "  %s=%s\n" % (key, value)
        return out


class KbInfo:
    def __init__(self):
        self.nDocumentVersion = -1
        self.nTagVersion = -1
        self.nStyleVersion = -1
        self.nAttachmentVersion = -1
        self.nDeletedGUIDVersion = -1
        self.nParamVersion = -1
        self.nUserVersion = -1

        self.nStorageLimit = 0
        self.nStorageUsage = 0
        self.nTrafficLimit = 0
        self.nTrafficUsage = 0
        self.nUploadSizeLimit = 30 * 1024 * 1024

    def fromJson(self, info_json):
        self.strKbGUID = info_json["kbGuid"]

        self.nStorageLimit = info_json["storageLimit"]
        self.nStorageUsage = info_json["storageUsage"]

        self.nTrafficLimit = info_json["trafficLimit"]
        self.nTrafficUsage = info_json["trafficUsage"]

        self.nUploadSizeLimit = info_json["uploadSizeLimit"]

        self.nNotesCount = info_json["noteCount"]
        self.nNotesCountLimit = info_json["noteCountLimit"]

        self.nDocumentVersion = info_json["docVersion"]
        self.nTagVersion = info_json["tagVersion"]
        self.nStyleVersion = info_json["styleVersion"]
        self.nAttachmentVersion = info_json["attVersion"]
        self.nDeletedGUIDVersion = info_json["deletedVersion"]
        self.nParamVersion = info_json["paramVersion"]
        self.nUserVersion = info_json["userVersion"]


class KbValueVersions:
    def __init__(self):
        self.inited = False
        self.versions = {}

    def fromJson(self, info_json):
        self.strKbGUID = info_json["kbGuid"]
        versionsVal = info_json["versions"]
        for version in versionsVal:
            key = version["key"]
            ver = version["version"]
            self.versions[key] = ver
        self.inited = True
