import base64
import json
import binascii
import re
import requests
import traceback
from utils import hex_to_oct_keys, extract_time, fix_time, TIMES_DICT

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
        # print(last_minute_dict)
        return last_minute_dict
    except Exception as e:
        print(f'(am) {e.__class__.__module__}.{e.__class__.__name__}: {e}')
        traceback.print_exc()
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

    title = "[AM] " + re.sub(r"\[/?[A-Z]+[^\]]*\]", "", item["title"], flags=re.IGNORECASE).strip()
    title = re.sub(r' ?\([^)(]+\)', '', title)
    if not any(time in title for time in list(dict.fromkeys(TIMES_DICT.values()))):
        title = fix_time(title)
    if any(s in manifest_url for s in ('.dazn.', '.daznedge.', '.indazn.')):
        title += ' [DAZN]'
    elif '_dazn_' in manifest_url:
        title += ' [DAZN-CH]'
    elif '_spalk_' in manifest_url:
        title += ' [SKY-CH]'
    elif '_blue_' in manifest_url:
        title += ' [BLUE SPORT]'

    item["title"] = title
    item["manifest_url"] = manifest_url
    item["kid_key_pair"] = kid_key_pair
    if headers:
        item["headers"] = headers
    del item["myresolve"]
    del item["thumbnail"]
    del item["fanart"]
    del item["info"]
    return item


def filter_items(channels_dict: dict) -> list[dict]:
    filtered_items = []
    for item in channels_dict["items"]:
        if "myresolve" in item:
            if "amstaff@@" in item["myresolve"] or any(x in item["myresolve"] for x in [".m3u8", ".mpd", ".livx"]):
                # Avoid linear channels
                if 'CH 01' in item["title"]:
                    break
                filtered_items.append(clean_item(item))
        elif 'volley' in item["info"].lower():
            break
    # sorted_by_time = sorted(filtered_items, key=lambda x: extract_time(x["title"]))
    return filtered_items


if __name__ == "__main__":
    channels_dict = getAmChannelsDict()
    filtered_items = filter_items(channels_dict)
    print(json.dumps(filtered_items, indent=4))
    print(f"✅ Found {len(filtered_items)} channels from AM.")
