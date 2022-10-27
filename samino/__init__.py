from .lib.exception import Except
from .client import Client
from .local import Local
from .acm import Acm
from requests import get

try:
    version = "2.3.8"
    newest = get("https://pypi.python.org/pypi/SAmino/json").json()["info"]["version"]
    if version != newest:
        print(f"\033[1;33mSAmino New Version!: {newest} (Your Using {version})\033[1;0m")
except (Exception, BaseException):
    pass
