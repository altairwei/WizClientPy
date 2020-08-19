import time

from wizclientpy.constants import TOKEN_TIMEOUT_INTERVAL


class UserInfo:
    """Represents user information."""
    def __init__(self, server, info_json):
        self.as_server = server
        self.fromJson(info_json)

    def fromJson(self, info_json):
        self.token = info_json["token"]
        self.kb_guid = info_json["kbGuid"]
        self.kb_server = info_json["kbServer"]
        self.my_wiz_email = info_json["mywizEmail"]
        self.user_level = info_json["userLevel"]
        self.user_level_name = info_json["userLevelName"]
        self.user_points = info_json["userPoints"]
        self.user_type = info_json["userType"]
        self.max_file_size = info_json["uploadSizeLimit"]

        self.invite_code = info_json["inviteCode"]
        self.notice_text = info_json["noticeText"]
        self.notice_link = info_json["noticeLink"]

        self.vip_expried = info_json["vipDate"]

        user = info_json["user"]
        self.user_email = user["email"]
        self.display_name = user["displayName"]
        self.user_guid = user["userGuid"]
        self.created = user["created"]

    def __str__(self):
        out = "[User '%s']\n" % self.display_name
        for key in self.__dict__:
            if key in ["created", "vip_expried"]:
                timestamp = self.__dict__[key]
                if timestamp:
                    value = time.asctime(time.localtime(timestamp/1000))
            else:
                value = self.__dict__[key]
            if value:
                out += "%s=%s\n" % (key, value)
        return out


class KbInfo:
    def __init__(self):
        self.document_version = -1
        self.tag_version = -1
        self.style_version = -1
        self.attachment_version = -1
        self.deleted_guid_version = -1
        self.param_version = -1
        self.user_version = -1

        self.storage_limit = 0
        self.storage_usage = 0
        self.traffic_limit = 0
        self.traffic_usage = 0
        self.upload_size_limit = 30 * 1024 * 1024

    def fromJson(self, info_json):
        self.kb_guid = info_json["kbGuid"]

        self.storage_limit = info_json["storageLimit"]
        self.storage_usage = info_json["storageUsage"]

        self.traffic_limit = info_json["trafficLimit"]
        self.traffic_usage = info_json["trafficUsage"]

        self.upload_size_limit = info_json["uploadSizeLimit"]

        self.nNotesCount = info_json["noteCount"]
        self.nNotesCountLimit = info_json["noteCountLimit"]

        self.document_version = info_json["docVersion"]
        self.tag_version = info_json["tagVersion"]
        self.style_version = info_json["styleVersion"]
        self.attachment_version = info_json["attVersion"]
        self.deleted_guid_version = info_json["deletedVersion"]
        self.param_version = info_json["paramVersion"]
        self.user_version = info_json["userVersion"]


class KbValueVersions:
    def __init__(self, info_json=None):
        self.inited = False
        self.versions = {}
        if info_json:
            self.fromJson(info_json)

    def fromJson(self, info_json):
        self.strKbGUID = info_json["kbGuid"]
        versionsVal = info_json["versions"]
        for version in versionsVal:
            key = version["key"]
            ver = version["version"]
            self.versions[key] = ver
        self.inited = True
