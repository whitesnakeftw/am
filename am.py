import base64
import json
import binascii
import re
import requests
import traceback
from utils import hex_to_oct_keys, extract_time, TIME_RE

HOME_URL = "https://test34344.herokuapp.com/filter.php"
PASSWORD = "MandraKodi3"
DEVICE_ID = "2K1WPN"
VERSION = "2.0.0"
MK_USER_AGENT = f"MandraKodi2@@{VERSION}@@{PASSWORD}@@{DEVICE_ID}"
HEADERS = {"User-Agent": MK_USER_AGENT}

TIMES_DICT = {
    '10:56': '12:30',
    '13:26': '15:00',
    '13:41': '15:00',
    '16:11': '18:00',
    '18:26': '20:45',
}


def fix_time(title_with_time: str) -> str:
    try:
        hours, minutes = TIME_RE.search(title_with_time).groups()
        if f'{hours}:{minutes}' in TIMES_DICT.keys():
            hours, minutes = TIMES_DICT[f'{hours}:{minutes}'].split(':')
        else:
            seconds = (int(hours) * 3600 + int(minutes) * 60) + 3600  # +1 hour
            hours = f'{seconds // 3600}'
            minutes = f'{(seconds % 3600) // 60:02d}'
    except AttributeError:
        return title_with_time
    return TIME_RE.sub(f'{hours}:{minutes}', title_with_time)


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

    item["title"] = "[AM] " + re.sub(r"\[/?[A-Z]+[^\]]*\]", "", item["title"], flags=re.IGNORECASE).strip()
    item["title"] = re.sub(r' ?\([^)(]+\)', '', item["title"])
    item["title"] = fix_time(item["title"])
    if '.dazn.' in manifest_url:
        item["title"] += ' [DAZN]'
    elif '_dazn_' in manifest_url:
        item["title"] += ' [DAZN-CH]'
    elif '_spalk_' in manifest_url:
        item["title"] += ' [SKY-CH]'
    elif '_blue_' in manifest_url:
        item["title"] += ' [BLUE SPORT]'

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
    sorted_by_time = sorted(filtered_items, key=lambda x: extract_time(x["title"]))
    return sorted_by_time


if __name__ == "__main__":
    channels_dict = getAmChannelsDict()
    filtered_items = filter_items(channels_dict)
    print(json.dumps(filtered_items, indent=4))
    print(f"✅ Found {len(filtered_items)} channels from AM.")
