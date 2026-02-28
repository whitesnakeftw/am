import base64
import binascii
import re
import requests
from utils import hex_to_oct_keys

HOME_URL = "https://test34344.herokuapp.com/filter.php"
PASSWORD = "MandraKodi3"
DEVICE_ID = "2K1WPN"
VERSION = "2.0.0"
MK_USER_AGENT = f"MandraKodi2@@{VERSION}@@{PASSWORD}@@{DEVICE_ID}"
HEADERS = {"User-Agent": MK_USER_AGENT}


def getAmChannelsDict() -> dict:
    try:
        home_dict = requests.get(HOME_URL, headers=HEADERS).json()
        sport_url = next((i for i in home_dict["items"] if i["info"].lower() == 'sport'))["externallink"]
        sport_dict = requests.get(sport_url, headers=HEADERS).json()
        last_minute_url = next((i for i in sport_dict["items"] if i["info"].lower() == 'last minute'))["externallink"]
        last_minute_dict = requests.get(last_minute_url, headers=HEADERS).json()
        return last_minute_dict
    except Exception as e:
        print('Exception:', e)
        return []


def clean_item(item: dict) -> dict:
    headers = None
    manifest_reference = item["myresolve"].rsplit("@@")[1].rsplit("|")[0]
    try:
        resolve = base64.b64decode(manifest_reference).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError):
        resolve = manifest_reference

    manifest_url = resolve.rsplit("|")[0].strip()

    if "|" in item["myresolve"]:
        kid_key_pair = item["myresolve"].rsplit("|")[1].strip()
    elif "|" in resolve:
        kid_key_pair = resolve.rsplit("|")[1].strip()
    if '=' in kid_key_pair:
        headers = kid_key_pair
        kid_key_pair = ""
    if ',' in kid_key_pair:
        kid_key_pair = hex_to_oct_keys(kid_key_pair)
    if len(kid_key_pair) < 64 or re.search(r'^0+:0+$', kid_key_pair):
        kid_key_pair = ""

    item["title"] = "[AM] " + re.sub(r"\[/?[A-Z]+[^\]]*\]", "", item["title"], flags=re.IGNORECASE).strip()
    item["manifest_url"] = manifest_url
    item["kid_key_pair"] = kid_key_pair
    if headers:
        item["headers"] = headers
    del item["myresolve"]
    del item["thumbnail"]
    del item["fanart"]
    del item["info"]
    return item


def has_time_in_title(title: str) -> bool:
    return bool(re.match(r'.*\b\d{1,2}:\d{2}\b', title))


def filter_items(channels_dict: dict) -> list[dict]:
    filtered_items = []
    for item in channels_dict["items"]:
        if "myresolve" in item:
            if "amstaff@@" in item["myresolve"] or any(x in item["myresolve"] for x in [".m3u8", ".mpd", ".livx"]):
                filtered_items.append(clean_item(item))
    # Move actual events first
    events = [i for i in filtered_items if has_time_in_title(i.get("title", ""))]
    # linear_channels = [i for i in filtered_items if not has_time_in_title(i.get("title", ""))]
    # ordered_items = events + linear_channels
    ordered_items = events
    return ordered_items


if __name__ == "__main__":
    channels_dict = getAmChannelsDict()
    filtered_items = filter_items(channels_dict)
    print(filtered_items)
    print(f"✅ Found {len(filtered_items)} channels from AM.")
