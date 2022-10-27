from time import time as timestamp

import ujson as json
from requests import Session

from .lib import *
from .lib import CheckExceptions
from .lib.objects import *


class Acm:
    def __init__(self, comId: str, proxies: dict = None):
        self.proxies = proxies
        self.comId = comId
        self.uid = headers.Headers().uid
        self.headers = headers.Headers().headers
        self.api = "https://service.narvii.com/api/v1"
        self.session = Session()

    def promote(self, userId: str, rank: str):
        rank = rank.lower()

        if rank not in ["agent", "leader", "curator"]:
            raise TypeError(rank)

        rank = rank.replace("agent", "transfer-agent")
        req = self.session.post(api(f"/x{self.comId}/s/user-profile/{userId}/{rank}"), headers=self.headers,
                                proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def accept_join_request(self, userId: str):
        req = self.session.post(api(f"/x{self.comId}/s/community/membership-request/{userId}/accept"),
                                headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def reject_join_request(self, userId: str):
        req = self.session.post(api(f"/x{self.comId}/s/community/membership-request/{userId}/reject"),
                                headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def change_welcome_message(self, message: str, enabled: bool = True):
        data = json.dumps({
            "path": "general.welcomeMessage",
            "value": {"enabled": enabled, "text": message},
            "timestamp": int(timestamp() * 1000)
        })
        req = self.session.post(api(f"/x{self.comId}/s/community/configuration"), data=data,
                                headers=headers.Headers(data=data).headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def change_guidelines(self, content: str):
        data = json.dumps({"content": content, "timestamp": int(timestamp() * 1000)})
        req = self.session.post(api(f"/x{self.comId}/s/community/guideline"),
                                headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def edit_community(self, name: str = None, description: str = None, aminoId: str = None, language: str = None,
                       themePackUrl: str = None):
        data = {"timestamp": int(timestamp() * 1000)}

        if name:
            data["name"] = name
        if description:
            data["content"] = description
        if aminoId:
            data["endpoint"] = aminoId
        if lang:
            data["primaryLanguage"] = lang
        if themePackUrl:
            data["themePackUrl"] = themePackUrl

        data = json.dumps(data)
        req = self.session.post(api(f"/x{self.comId}/s/community/settings"), data=data,
                                headers=headers.Headers(data=data).headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def get_community_stats(self):
        req = self.session.get(api(f"/x{self.comId}/s/community/stats"), headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return CommunityStats(req.json()["communityStats"]).CommunityStats

    def get_admin_stats(self, type: str, start: int = 0, size: int = 25):
        if type not in ["leader", "curator"]:
            raise TypeError(type)

        req = self.session.get(
            api(f"/x{self.comId}/s/community/stats/moderation?type={type}&start={start}&size={size}"),
            headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def get_join_requests(self, start: int = 0, size: int = 25):
        req = self.session.get(
            api(f"/x{self.comId}/s/community/membership-request?status=pending&start={start}&size={size}"),
            headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return JoinRequest(req.json()).JoinRequest

    def get_all_members(self, type: str, start: int = 0, size: int = 25):
        type = type.lower()
        req = self.session.get(api(f"/x{self.comId}/s/user-profile?type={type}&start={start}&size={size}"),
                               headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return UserProfileList(req.json()["userProfileList"]).UserProfileList

    def add_influencer(self, userId: str, monthlyFee: int = 50):
        data = json.dumps({"monthlyFee": monthlyFee, "timestamp": int(timestamp() * 1000)})
        req = self.session.post(api(f"/x{self.comId}/s/influencer/{userId}"), data=data,
                                headers=headers.Headers(data=data).headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def remove_influencer(self, userId: str):
        req = self.session.delete(api(f"/x{self.comId}/s/influencer/{userId}"), headers=self.headers,
                                  proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())
