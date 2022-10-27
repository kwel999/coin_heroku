import os
from binascii import hexlify
from time import time as timestamp
from typing import BinaryIO
from typing import Union
from uuid import UUID
from requests import Session

import ujson as json

from .lib import *
from .lib import CheckExceptions
from .lib.objects import *
from .sockets import Wss


class Client(Wss):
    def __init__(self, deviceId: str = None, proxies: str = {'http': 'socks5://92.246.119.175:8111','https':'socks5://92.246.119.175:8111'}, trace: bool = False):
        self.sid = None
        self.web_headers = None
        self.trace = trace
        self.proxies = proxies
        self.uid = None
        self.secret = None
        headers.deviceId = deviceId
        Wss.__init__(self, self, trace=self.trace)
        self.deviceId = headers.Headers().deviceId
        self.headers = headers.Headers().headers
        self.session = Session()

    def change_lang(self, lang: str = "ar-SY"):
        headers.lang = lang
        self.headers = headers.Headers().headers

    def sid_login(self, sid: str):
        headers.sid = sid

        if "sid=" not in sid:
            headers.sid = f"sid={sid}"

        self.headers = headers.Headers().headers

        try:
            info = self.get_account_info().userId
            self.uid = info
            self.sid = headers.sid
            headers.uid = self.uid
            self.launch()
            return info
        except Exception as e:
            print(f"\nError getting user info in sid_login: {e}\n")

    def login(self, email: str = None, password: str = None, secret: str = None, socket: bool = False):
        data = {
            "clientType": 100,
            "action": "normal",
            "deviceID": self.deviceId,
            "v": 2,
            "timestamp": int(timestamp() * 1000)
        }

        if password and email and not secret:
            data["email"] = email
            data["secret"] = f"0 {password}"
        elif secret:
            data["secret"] = secret
        else:
            raise ValueError(
                "When using a password, email is required. when using a secret, email is not required. so please insert the email with the password")

        data = json.dumps(data)
        req = self.session.post(api(f"/g/s/auth/login"), headers=headers.Headers(data=data).headers,
                                proxies=self.proxies, data=data)

        if req.status_code != 200:
            return CheckExceptions(req.json())

        self.sid = f'sid={req.json()["sid"]}'
        self.uid = req.json()["auid"]
        self.headers["NDCAUTH"] = self.sid
        self.secret = req.json()["secret"]
        headers.sid = self.sid
        headers.uid = self.uid
        self.headers = headers.Headers().headers
        self.web_headers = headers.Headers().web_headers

        if socket:
            self.launch()

        return Login(req.json())

    def logout(self):
        data = json.dumps({
            "deviceID": self.deviceId,
            "clientType": 100,
            "timestamp": int(timestamp() * 1000)
        })

        req = self.session.post(api("/g/s/auth/logout"), headers=headers.Headers(data=data).headers, data=data,
                                proxies=self.proxies)
        if req.status_code != 200:
            return CheckExceptions(req.json())
        else:
            self.sid = None
            self.uid = None
            headers.sid = None
            headers.uid = None

            if self.isOpened:
                self.close()

            return Json(req.json())

    def check_device(self, deviceId: str = "42018060F4195790EE4AF93B2E844F46635DFABA92CF933D1CDC5F8AE8CDC00BC1FFAA1205BC2FF172") -> str:
        data = json.dumps({
            "deviceID": deviceId,
            "timestamp": int(timestamp() * 1000),
            "clientType": 100
        })
        self.headers["NDCDEVICEID"] = deviceId
        req = self.session.post(api(f"/g/s/device/"), headers=headers.Headers(data=data).headers, data=data)
        if req.json()["api:statuscode"] != 0: return CheckExceptions(req.json())
        return f"api:message {req.json()['api:message']}\napi:statuscode {req.json()['api:statuscode']}\nThe device is fine"

    def upload_image(self, image: BinaryIO):
        data = image.read()

        self.headers["content-type"] = "image/jpg"
        self.headers["content-length"] = str(len(data))

        req = self.session.post(api(f"/g/s/media/upload"), data=data, headers=self.headers, proxies=self.proxies)
        return req.json()["mediaValue"]

    def send_verify_code(self, email: str):
        data = json.dumps({
            "identity": email,
            "type": 1,
            "deviceID": self.deviceId,
            "timestamp": int(timestamp() * 1000)
        })
        req = self.session.post(api(f"/g/s/auth/request-security-validation"),
                                headers=headers.Headers(data=data).headers,
                                proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def accept_host(self, requestId: str, chatId: str):
        req = self.session.post(api(f"/g/s/chat/thread/{chatId}/transfer-organizer/{requestId}/accept"),
                                headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def verify_account(self, email: str, code: str):
        data = json.dumps({
            "type": 1,
            "identity": email,
            "data": {"code": code},
            "deviceID": self.deviceId
        })
        req = self.session.post(api(f"/g/s/auth/activate-email"), headers=headers.Headers(data=data).headers,
                                proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def restore(self, email: str, password: str):
        data = json.dumps({
            "secret": f"0 {password}",
            "deviceID": self.deviceId,
            "email": email,
            "timestamp": int(timestamp() * 1000)
        })

        req = self.session.post(api(f"/g/s/account/delete-request/cancel"), headers=headers.Headers(data=data).headers,
                                proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def delete_account(self, password: str = None):
        data = json.dumps({
            "deviceID": self.deviceId,
            "secret": f"0 {password}",
            "timestamp": int(timestamp() * 1000)
        })

        req = self.session.post(api(f"/g/s/account/delete-request"), headers=headers.Headers(data=data).headers,
                                proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def get_account_info(self):
        req = self.session.get(api(f"/g/s/account"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Account(req.json()["account"])

    def claim_coupon(self):
        req = self.session.post(api(f"/g/s/coupon/new-user-coupon/claim"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def change_amino_id(self, aminoId: str = None):
        data = json.dumps({"aminoId": aminoId, "timestamp": int(timestamp() * 1000)})
        req = self.session.post(api(f"/g/s/account/change-amino-id"), data=data,
                                headers=headers.Headers(data=data).headers,
                                proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def get_my_communitys(self, start: int = 0, size: int = 25):
        req = self.session.get(api(f"/g/s/community/joined?v=1&start={start}&size={size}"), headers=self.headers,
                               proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return CommunityList(req.json()["communityList"]).CommunityList

    def get_chat_threads(self, start: int = 0, size: int = 25):
        req = self.session.get(api(f"/g/s/chat/thread?type=joined-me&start={start}&size={size}"), headers=self.headers,
                               proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return ThreadList(req.json()["threadList"]).ThreadList

    def get_chat_info(self, chatId: str):
        req = self.session.get(api(f"/g/s/chat/thread/{chatId}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Thread(req.json()["thread"]).Thread

    def leave_chat(self, chatId: str):
        req = self.session.delete(api(f"/g/s/chat/thread/{chatId}/member/{self.uid}"), headers=self.headers,
                                  proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def join_chat(self, chatId: str):
        req = self.session.post(api(f"/g/s/chat/thread/{chatId}/member/{self.uid}"), headers=self.headers,
                                proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def start_chat(self, userId: Union[str, list], title: str = None, message: str = None, content: str = None,
                   chatType: int = 0):

        if type(userId) is list:
            userIds = userId
        elif type(userId) is str:
            userIds = [userId]
        else:
            raise TypeError("Please put a str or list of userId")

        data = json.dumps({
            "title": title,
            "inviteeUids": userIds,
            "initialMessageContent": message,
            "content": content,
            "type": chatType,
            "timestamp": int(timestamp() * 1000)
        })

        req = self.session.post(api(f"/g/s/chat/thread"), headers=headers.Headers(data=data).headers,
                                proxies=self.proxies,
                                data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def get_from_link(self, link: str):
        req = self.session.get(api(f"/g/s/link-resolution?q={link}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return FromCode(req.json()["linkInfoV2"]["extensions"]).FromCode

    def edit_profile(self, nickname: str = None, content: str = None, icon: BinaryIO = None,
                     backgroundColor: str = None, backgroundImage: str = None, defaultBubbleId: str = None):
        data = {
            "address": None,
            "latitude": 0,
            "longitude": 0,
            "mediaList": None,
            "eventSource": "UserProfileView",
            "timestamp": int(timestamp() * 1000)
        }

        if nickname: data["nickname"] = nickname
        if icon: data["icon"] = self.upload_image(icon)
        if content: data["content"] = content
        if backgroundColor: data["extensions"]["style"] = {"backgroundColor": backgroundColor}
        if backgroundImage: data["extensions"]["style"] = {
            "backgroundMediaList": [[100, backgroundImage, None, None, None]]}
        if defaultBubbleId: data["extensions"] = {"defaultBubbleId": defaultBubbleId}

        data = json.dumps(data)
        req = self.session.post(api(f"/g/s/user-profile/{self.uid}"), headers=headers.Headers(data=data).headers,
                                proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def flag_community(self, comId: str, reason: str, flagType: int):
        data = json.dumps({
            "objectId": comId,
            "objectType": 16,
            "flagType": flagType,
            "message": reason,
            "timestamp": int(timestamp() * 1000)
        })
        req = self.session.post(api(f"/x{comId}/s/g-flag"), headers=headers.Headers(data=data).headers,
                                proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def leave_community(self, comId: str):
        req = self.session.post(api(f"/x{comId}/s/community/leave"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def join_community(self, comId: str, InviteId: str = None):
        data = {"timestamp": int(timestamp() * 1000)}
        if InviteId: data["invitationId"] = InviteId
        data = json.dumps(data)
        req = self.session.post(api(f"/x{comId}/s/community/join"), data=data,
                                headers=headers.Headers(data=data).headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def flag(self, reason: str, type: str = "spam", userId: str = None, wikiId: str = None, blogId: str = None):
        types = {
            "violence": 106,
            "hate": 107,
            "suicide": 108,
            "troll": 109,
            "nudity": 110,
            "bully": 0,
            "off-topic": 4,
            "spam": 2
        }

        data = {
            "message": reason,
            "timestamp": int(timestamp() * 1000)
        }

        if type in types:
            data["flagType"] = types.get(type)
        else:
            raise TypeError("choose a certain type to report")

        if userId:
            data["objectId"] = userId
            data['objectType'] = 0

        elif blogId:
            data["objectId"] = blogId
            data['objectType'] = 1

        elif wikiId:
            data["objectId"] = wikiId
            data["objectType"] = 2

        else:
            raise TypeError("Please put blog or user or wiki Id")

        data = json.dumps(data)
        req = self.session.post(
            api(f"/g/s/flag", headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data))
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def unfollow(self, userId: str):
        req = self.session.post(api(f"/g/s/user-profile/{userId}/member/{self.uid}"), headers=self.headers,
                                proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def follow(self, userId: Union[str, list]):
        if type(userId) is str:
            req = self.session.post(api(f"/g/s/user-profile/{userId}/member"), headers=self.headers,
                                    proxies=self.proxies)
        elif type(userId) is list:
            data = json.dumps({"targetUidList": userId, "timestamp": int(timestamp() * 1000)})
            req = self.session.post(api(f"/g/s/user-profile/{self.uid}/joined"),
                                    headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        else:
            raise TypeError("Please put a str or list of userId")

        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def get_member_following(self, userId: str, start: int = 0, size: int = 25):
        req = self.session.get(api(f"/g/s/user-profile/{userId}/joined?start={start}&size={size}"),
                               headers=self.headers,
                               proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return UserProfileList(req.json()["userProfileList"]).UserProfileList

    def get_member_followers(self, userId: str, start: int = 0, size: int = 25):
        req = self.session.get(api(f"/g/s/user-profile/{userId}/member?start={start}&size={size}"),
                               headers=self.headers,
                               proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return UserProfileList(req.json()["userProfileList"]).UserProfileList

    def get_member_visitors(self, userId: str, start: int = 0, size: int = 25):
        req = self.session.get(api(f"/g/s/user-profile/{userId}/visitors?start={start}&size={size}"),
                               headers=self.headers,
                               proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return VisitorsList(req.json()["visitors"]).VisitorsList

    def get_blocker_users(self, start: int = 0, size: int = 25):
        req = self.session.get(api(f"/g/s/block/full-list?start={start}&size={size}"), headers=self.headers,
                               proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return req.json()["blockerUidList"]

    def get_blocked_users(self, start: int = 0, size: int = 25):
        req = self.session.get(api(f"/g/s/block/full-list?start={start}&size={size}"), headers=self.headers,
                               proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return req.json()["blockedUidList"]

    def get_wall_comments(self, userId: str, sorting: str = 'newest', start: int = 0, size: int = 25):
        sorting = sorting.lower()
        if sorting == 'top': sorting = "vote"
        if sorting not in ["newest", "oldest", "vote"]: raise TypeError("حط تايب يا حمار")

        req = self.session.get(api(f"/g/s/user-profile/{userId}/g-comment?sort={sorting}&start={start}&size={size}"),
                               headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return CommentList(req.json()["commentList"]).CommentList

    def get_blog_comments(self, wikiId: str = None, blogId: str = None, sorting: str = "newest", size: int = 25,
                          start: int = 0):
        sorting = sorting.lower()
        url = None

        if sorting == "top":
            sorting = "vote"
        if sorting not in ["newest", "oldest", "vote"]:
            raise TypeError("Please insert a valid sorting")
        if blogId:
            url = api(f"/g/s/blog/{blogId}/comment?sort={sorting}&start={start}&size={size}")
        elif wikiId:
            url = api(f"/g/s/item/{wikiId}/comment?sort={sorting}&start={start}&size={size}")

        req = self.session.get(url, headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return CommentList(req.json()["commentList"]).CommentList

    def send_message(self, chatId: str, message: str = None, messageType: int = 0, file: BinaryIO = None,
                     fileType: str = None, replyTo: str = None, mentionUserIds: Union[list, str] = None, stickerId: str = None,
                     snippetLink: str = None, ytVideo: str = None, snippetImage: BinaryIO = None, embedId: str = None,
                     embedType: int = None, embedLink: str = None, embedTitle: str = None, embedContent: str = None,
                     embedImage: BinaryIO = None):
                     
        if message is not None and file is None: message = message.replace("[@", "‎‏").replace("@]", "‬‭")

        mentions = []
        if mentionUserIds:
            if type(mentionUserIds) is list:
                for mention_uid in mentionUserIds: mentions.append({"uid": mention_uid})
            mentions.append({"uid": mentionUserIds})

        if embedImage:
            if type(embedImage) is not str: embedImage = [[100, self.upload_image(embedImage), None]]
            embedImage = [[100, embedImage, None]]

        data = {
            "type": messageType,
            "content": message,
            "attachedObject": {
                "objectId": embedId,
                "objectType": embedType,
                "link": embedLink,
                "title": embedTitle,
                "content": embedContent,
                "mediaList": embedImage
            },
            "extensions": {"mentionedArray": mentions},
            "clientRefId": int(timestamp() / 10 % 100000000),
            "timestamp": int(timestamp() * 1000)
        }

        if replyTo: data["replyMessageId"] = replyTo

        if stickerId:
            data["content"] = None
            data["stickerId"] = stickerId
            data["type"] = 3

        if snippetLink and snippetImage:
            data["attachedObject"] = None
            data["extensions"]["linkSnippetList"] = [{
                "link": snippetLink,
                "mediaType": 100,
                "mediaUploadValue": base64.b64encode(snippetImage.read()).decode(),
                "mediaUploadValueContentType": "image/png"
            }]

        if ytVideo:
            data["content"] = None
            data["mediaType"] = 103
            data["mediaValue"] = ytVideo

        if file:
            data["content"] = None
            if fileType == "audio":
                data["type"] = 2
                data["mediaType"] = 110

            elif fileType == "image":
                data["mediaType"] = 100
                data["mediaUploadValueContentType"] = "image/jpg"
                data["mediaUhqEnabled"] = False

            elif fileType == "gif":
                data["mediaType"] = 100
                data["mediaUploadValueContentType"] = "image/gif"
                data["mediaUhqEnabled"] = False

            else:
                raise TypeError(fileType)

            data["mediaUploadValue"] = base64.b64encode(file.read()).decode()
            data["attachedObject"] = None
            data["extensions"] = None

        data = json.dumps(data)
        req = self.session.post(api(f"/g/s/chat/thread/{chatId}/message"),
                                headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def get_community_info(self, comId: str):
        req = self.session.get(
            api(f"/g/s-x{comId}/community/info?withInfluencerList=1&withTopicList=true&influencerListOrderStrategy=fansCount"),
            headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Community(req.json()["community"]).Community

    def mark_as_read(self, chatId: str):
        req = self.session.post(api(f"/g/s/chat/thread/{chatId}/mark-as-read"), headers=self.headers,
                                proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def delete_message(self, messageId: str, chatId: str):
        req = self.session.delete(api(f"/g/s/chat/thread/{chatId}/message/{messageId}"), headers=self.headers,
                                  proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def get_chat_messages(self, chatId: str, start: int = 0, size: int = 25):
        req = self.session.get(api(f"/g/s/chat/thread/{chatId}/message?v=2&pagingType=t&size={size}"),
                               headers=self.headers,
                               proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return GetMessages(req.json()["messageList"]).GetMessages

    def get_message_info(self, messageId: str, chatId: str):
        req = self.session.get(api(f"/g/s/chat/thread/{chatId}/message/{messageId}"), headers=self.headers,
                               proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Message(req.json()["message"]).Message

    def tip_coins(self, chatId: str = None, blogId: str = None, coins: int = 0, transactionId: str = None):
        if transactionId is None: transactionId = str(UUID(hexlify(os.urandom(16)).decode("ascii")))
        data = json.dumps({
            "coins": coins,
            "tippingContext": {
                "transactionId": transactionId
            },
            "timestamp": int(timestamp() * 1000)
        })

        if chatId:
            url = api(f"/g/s/blog/{chatId}/tipping")
        elif blogId:
            url = api(f"/g/s/blog/{blogId}/tipping")
        else:
            raise TypeError("please put chat or blog Id")

        req = self.session.post(url, headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def reset_password(self, email: str, password: str, code: str, deviceId: str = None):
        if deviceId is None: deviceId = self.deviceId

        data = json.dumps({
            "updateSecret": f"0 {password}",
            "emailValidationContext": {
                "data": {
                    "code": code
                },
                "type": 1,
                "identity": email,
                "level": 2,
                "deviceID": deviceId
            },
            "phoneNumberValidationContext": None,
            "deviceID": deviceId,
            "timestamp": int(timestamp() * 1000)
        })

        req = self.session.post(api(f"/g/s/auth/reset-password"), headers=headers.Headers(data=data).headers,
                                proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def change_password(self, password: str, newPassword: str):
        data = json.dumps({
            "secret": f"0 {password}",
            "updateSecret": f"0 {newPassword}",
            "validationContext": None,
            "deviceID": self.deviceId
        })
        header = headers.Headers(data=data).headers
        header["ndcdeviceid"], header["ndcauth"] = header["NDCDEVICEID"], header["NDCAUTH"]
        req = self.session.post(api("/g/s/auth/change-password"), headers=header, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def get_user_info(self, userId: str):
        req = self.session.get(api(f"/g/s/user-profile/{userId}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return UserProfile(req.json()["userProfile"]).UserProfile

    def comment(self, comment: str, userId: str = None, replyTo: str = None):
        data = {
            "content": comment,
            "stickerId": None,
            "type": 0,
            "eventSource": "UserProfileView",
            "timestamp": int(timestamp() * 1000)
        }

        if replyTo: data["respondTo"] = replyTo

        data = json.dumps(data)

        req = self.session.post(api(f"/g/s/user-profile/{userId}/g-comment"),
                                headers=headers.Headers(data=data).headers,
                                proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def delete_comment(self, userId: str = None, commentId: str = None):
        req = self.session.delete(api(f"/g/s/user-profile/{userId}/g-comment/{commentId}"), headers=self.headers,
                                  proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def invite_by_host(self, chatId: str, userId: Union[str, list]):
        data = json.dumps({"uidList": userId, "timestamp": int(timestamp() * 1000)})

        req = self.session.post(api(f"/g/s/chat/thread/{chatId}/avchat-members"),
                                headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def kick(self, chatId: str, userId: str, rejoin: bool = True):
        if rejoin: rejoin = 1
        if not rejoin: rejoin = 0

        req = self.session.delete(api(f"/g/s/chat/thread/{chatId}/member/{userId}?allowRejoin={rejoin}"),
                                  headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def block(self, userId: str):
        req = self.session.post(api(f"/g/s/block/{userId}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def unblock(self, userId: str):
        req = self.session.delete(api(f"/g/s/block/{userId}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def get_public_chats(self, type: str = "recommended", start: int = 0, size: int = 50):
        req = self.session.get(api(f"/g/s/chat/thread?type=public-all&filterType={type}&start={start}&size={size}"),
                               headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return ThreadList(req.json()["threadList"]).ThreadList

    def get_content_modules(self, version: int = 2):
        req = self.session.get(api(f"/g/s/home/discover/content-modules?v={version}"), headers=self.headers,
                               proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def get_banner_ads(self, size: int = 25, pagingType: str = "t"):
        req = self.session.get(
            api(f"/g/s/topic/0/feed/banner-ads?moduleId=711f818f-da0c-4aa7-bfa6-d5b58c1464d0&adUnitId=703798&size={size}&pagingType={pagingType}"),
            headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return ItemList(req.json()["itemList"]).ItemList

    def get_announcements(self, lang: str = "ar", start: int = 0, size: int = 20):
        req = self.session.get(api(f"/g/s/announcement?language={lang}&start={start}&size={size}"),
                               headers=self.headers,
                               proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return BlogList(req.json()["blogList"]).BlogList

    def get_discover(self, type: str = "discover", category: str = "customized", size: int = 25, pagingType: str = "t"):
        req = self.session.get(
            api(f"/g/s/topic/0/feed/community?type={type}&categoryKey={category}&moduleId=64da14e8-0845-47bf-946a-17403bd6aa17&size={size}&pagingType={pagingType}"),
            headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return CommunityList(req.json()["communityList"]).CommunityList

    def search_community(self, word: str, lang: str = "ar", start: int = 0, size: int = 25):
        req = self.session.get(
            api(f"/g/s/community/search?q={word}&language={lang}&completeKeyword=1&start={start}&size={size}"),
            headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return CommunityList(req.json()["communityList"]).CommunityList

    def invite_to_voice_chat(self, userId: str = None, chatId: str = None):
        data = json.dumps({"uid": userId, "timestamp": int(timestamp() * 1000)})
        req = self.session.post(api(f"/g/s/chat/thread/{chatId}/vvchat-presenter/invite"),
                                headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def get_wallet_history(self, start: int = 0, size: int = 25):
        req = self.session.get(api(f"/g/s/wallet/coin/history?start={start}&size={size}"), headers=self.headers,
                               proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return WalletHistory(req.json()).WalletHistory

    def get_wallet_info(self):
        req = self.session.get(api(f"/g/s/wallet"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return WalletInfo(req.json()["wallet"]).WalletInfo

    def get_all_users(self, type: str = "recent", start: int = 0, size: int = 25):
        """
        Types:
            - recent
            - banned
            - featured
            - leaders
            - curators
        """
        req = self.session.get(api(f"/g/s/user-profile?type={type}&start={start}&size={size}"), headers=self.headers,
                               proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return UserProfileList(req.json()["userProfileList"]).UserProfileList

    def get_chat_members(self, start: int = 0, size: int = 25, chatId: str = None):
        req = self.session.get(api(f"/g/s/chat/thread/{chatId}/member?start={start}&size={size}&type=default&cv=1.2"),
                               headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return UserProfileList(req.json()["memberList"]).UserProfileList

    def get_from_id(self, id: str, comId: str = None, objectType: int = 2):  # never tried
        data = json.dumps({
            "objectId": id,
            "targetCode": 1,
            "objectType": objectType,
            "timestamp": int(timestamp() * 1000)
        })

        if comId:
            url = api(f"/g/s-x{comId}/link-resolution")
        else:
            url = api(f"/g/s/link-resolution")

        req = self.session.post(url, headers=headers.Headers(data=data).headers, proxies=self.proxies, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return FromCode(req.json()["linkInfoV2"]["extensions"]["linkInfo"]).FromCode

    def chat_settings(self, chatId: str, viewOnly: bool = None, doNotDisturb: bool = None, canInvite: bool = False,
                      canTip: bool = None, pin: bool = None):
        res = []

        if doNotDisturb:
            if doNotDisturb:
                opt = 2
            else:
                opt = 1
            data = json.dumps({"alertOption": opt, "timestamp": int(timestamp() * 1000)})
            req = self.session.post(api(f"/g/s/chat/thread/{chatId}/member/{self.uid}/alert"), data=data,
                                    headers=headers.Headers(data=data).headers, proxies=self.proxies)
            if req.status_code != 200: return CheckExceptions(req.json())
            res.append(Json(req.json()))

        if viewOnly is not None:
            if viewOnly:
                viewOnly = "enable"
            else:
                viewOnly = "disable"
            req = self.session.post(api(f"/g/s/chat/thread/{chatId}/view-only/{viewOnly}"), headers=self.headers,
                                    proxies=self.proxies)
            if req.status_code != 200: return CheckExceptions(req.json())
            res.append(Json(req.json()))

        if canInvite:
            if canInvite:
                canInvite = "enable"
            else:
                canInvite = "disable"
            req = self.session.post(api(f"/g/s/chat/thread/{chatId}/members-can-invite/{canInvite}"),
                                    headers=self.headers,
                                    proxies=self.proxies)
            if req.status_code != 200: return CheckExceptions(req.json())
            res.append(Json(req.json()))

        if canTip:
            if canTip:
                canTip = "enable"
            else:
                canTip = "disable"
            req = self.session.post(api(f"/g/s/chat/thread/{chatId}/tipping-perm-status/{canTip}"),
                                    headers=self.headers,
                                    proxies=self.proxies)
            if req.status_code != 200: return CheckExceptions(req.json())
            res.append(Json(req.json()))

        if pin:
            if pin:
                pin = "pin"
            else:
                pin = "unpin"
            req = self.session.post(api(f"/g/s/chat/thread/{chatId}/{pin}"), headers=self.headers, proxies=self.proxies)
            if req.status_code != 200: return CheckExceptions(req.json())
            res.append(Json(req.json()))

        return res

    def like_comment(self, commentId: str, userId: str = None, blogId: str = None):
        data = json.dumps({"value": 4, "timestamp": int(timestamp() * 1000)})

        if userId:
            url = api(f"/g/s/user-profile/{userId}/comment/{commentId}/g-vote?cv=1.2&value=1")
        elif blogId:
            url = api(f"/g/s/blog/{blogId}/comment/{commentId}/g-vote?cv=1.2&value=1")
        else:
            raise TypeError("Please put blog or user Id")

        req = self.session.post(url, data=data, headers=headers.Headers(data=data).headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def unlike_comment(self, commentId: str, blogId: str = None, userId: str = None):
        if userId:
            url = api(f"/g/s/user-profile/{userId}/comment/{commentId}/g-vote?eventSource=UserProfileView")
        elif blogId:
            url = api(f"/g/s/blog/{blogId}/comment/{commentId}/g-vote?eventSource=PostDetailView")
        else:
            raise TypeError("Please put blog or user Id")

        req = self.session.delete(url, headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def register(self, nickname: str, email: str, password: str, deviceId: str = None):
        if deviceId is None: deviceId = self.deviceId

        data = json.dumps({
            "secret": f"0 {password}",
            "deviceID": deviceId,
            "email": email,
            "clientType": 100,
            "nickname": nickname,
            "latitude": 0,
            "longitude": 0,
            "address": None,
            "clientCallbackURL": "narviiapp://relogin",
            "type": 1,
            "identity": email,
            "timestamp": int(timestamp() * 1000)
        })

        req = self.session.post(api(f"/g/s/auth/register"), data=data, headers=headers.Headers(data=data).headers,
                                proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def remove_host(self, chatId: str, userId: str):
        req = self.session.delete(api(f"/g/s/chat/thread/{chatId}/co-host/{userId}"), headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def edit_comment(self, commentId: str, comment: str, userId: str):
        data = {"content": comment, "timestamp": int(timestamp() * 1000)}
        data = json.dumps(data)
        req = self.session.post(api(f"/g/s/user-profile/{userId}/comment/{commentId}"), data=data,
                                headers=headers.Headers(data=data).headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Comment(req.json()).Comments

    def get_comment_info(self, commentId: str, userId: str):
        req = self.session.get(api(f"/g/s/user-profile/{userId}/comment/{commentId}"), headers=self.headers,
                               proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Comment(req.json()).Comments

    def get_notifications(self, size: int = 25, pagingType: str = "t"):
        req = self.session.get(api(f"/g/s/notification?pagingType={pagingType}&size={size}"), headers = self.headers, proxies = self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return NotificationList(req.json()).NotificationList
    
    def get_notices(self, start: int = 0, size: int = 25, type: str = "usersV2", status: int = 1):
        req = self.session.get(api(f"/g/s/notice?type={type}&status={status}&start={start}&size={size}"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return NoticeList(req.json()).NoticeList

    def accept_promotion(self, requestId: str):
        if not isinstance(requestId, str): raise Exception(f"Please use a string not {type(requestId)}")
        req = self.session.post(api(f"/g/s/notice/{requestId}/accept"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())
    
    def decline_promotion(self, requestId: str):
        if not isinstance(requestId, str): raise Exception(f"Please use a string not {type(requestId)}")
        req = self.session.post(api(f"/g/s/notice/{requestId}/decline"), headers=self.headers, proxies=self.proxies)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())
