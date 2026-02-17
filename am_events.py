import base64
import binascii
import re
import requests

OUTFILE = "last_minute.m3u8"
HOME_URL = "https://test34344.herokuapp.com/filter.php"
PASSWORD = "MandraKodi3"
DEVICE_ID = "2K1WPN"
VERSION = "2.0.0"
USER_AGENT = f"MandraKodi2@@{VERSION}@@{PASSWORD}@@{DEVICE_ID}"
HEADERS = {"User-Agent": USER_AGENT}


def hex_to_oct_keys(hex_string):
    def _hex_to_base64url(hex_str: str):
        decoded_bytes = bytes.fromhex(hex_str)  # Convert hex string to bytes
        base64url_str = base64.urlsafe_b64encode(decoded_bytes).decode('utf-8')  # Encode bytes to Base64URL
        base64url_str = base64url_str.rstrip('=')  # Remove any padding ('=') characters
        return base64url_str

    def _extract_kid_k(kid_key_pair: str):
        kid_key_pair = kid_key_pair.replace('{', '').replace('}', '').replace(',', '').replace('"', '').replace("'", "").replace('-', '')
        kid = _hex_to_base64url(kid_key_pair.split(':')[0])
        key = _hex_to_base64url(kid_key_pair.split(':')[1])
        return kid, key

    for delim in (',', ' '):
        if delim in hex_string:
            pairs_list = [item for item in hex_string.split(delim) if item.strip()]  # if item.strip() removes empty arguments
            break
    result = ""
    for item in pairs_list:
        result += '{"kty":"oct","kid":"%s","k":"%s"}' % (*_extract_kid_k(item),)
    oct_keys = '{"keys":[%s]}' % result.replace('}{', '},{')
    return oct_keys


def get_channels_dict():
    home_dict = requests.get(HOME_URL, headers=HEADERS).json()
    sport_url = next((i for i in home_dict["items"] if i["info"].lower() == 'sport'))["externallink"]
    sport_dict = requests.get(sport_url, headers=HEADERS).json()
    last_minute_url = next((i for i in sport_dict["items"] if i["info"].lower() == 'last minute'))["externallink"]
    last_minute_dict = requests.get(last_minute_url, headers=HEADERS).json()
    return last_minute_dict


def clean_item(item):
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
    if len(kid_key_pair) < 64:
        kid_key_pair = ""

    item["title"] = re.sub(r"\[/?[A-Z]+[^\]]*\]", "", item["title"], flags=re.IGNORECASE).strip()
    item["manifest_url"] = manifest_url
    item["kid_key_pair"] = kid_key_pair
    if headers:
        item["headers"] = headers
    del item["myresolve"]
    del item["thumbnail"]
    del item["fanart"]
    del item["info"]
    return item


def filter_items(my_dict):
    filtered_items = []
    for item in my_dict["items"]:
        if "myresolve" in item:
            if "amstaff@@" in item["myresolve"] or any(x in item["myresolve"] for x in [".m3u8", ".mpd", ".livx"]):
                filtered_items.append(clean_item(item))
    return filtered_items


def create_m3u_entry(item):
    entry = f'#EXTINF:-1 group-title="ULTIMO MINUTO",{item["title"]}'
    if item.get("headers"):
        entry += f"\n#KODIPROP:inputstream.adaptive.stream_headers={item['headers']}"
    if item["kid_key_pair"]:
        entry += f"\n#KODIPROP:inputstream.adaptive.license_type=clearkey\n#KODIPROP:inputstream.adaptive.license_key={item['kid_key_pair']}"
    entry += f"\n{item['manifest_url']}"
    if item.get("headers"):
        entry += f"?|{item['headers']}"
    return entry


def create_m3u8_playlist(entries):
    playlist = "#EXTM3U\n\n"
    for entry in entries:
        playlist += create_m3u_entry(entry) + "\n\n"
    return playlist


filtered_items = filter_items(get_channels_dict())
with open(OUTFILE, 'w', encoding='utf-8') as f:
    f.write(create_m3u8_playlist(filtered_items))
print(f"✅ Playlist {OUTFILE} created with {len(filtered_items)} entries.")
