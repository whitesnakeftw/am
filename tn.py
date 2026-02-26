import requests
import re
import json
import base64
from datetime import datetime
from urllib.parse import unquote
from utils import hex_to_oct_keys

headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9,it;q=0.8,hu;q=0.7',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://thisnot.business/eventi.php',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
}


def login_to_site(url, password):
    try:
        session = requests.Session()
        response = session.post(url, data={'password': password})
        response.raise_for_status()
        return session
    except Exception as e:
        print(f'Login error: {e}')
        return None


def unpackKeys(keys: str) -> str:
    try:
        keys = ','.join(f'{kid}:{key}' for kid, key in json.loads(keys).items())
    except json.JSONDecodeError:
        pass
    return keys


def parseEventUrl(url: str, session: requests.Session) -> tuple[str, str, dict]:
    keys = None
    headers_dict = None
    try:
        response = session.get(url).text.replace('&amp;', '&')
        matches = re.search(r'pages/player\.html#(http(?:(?![?&](?:ck|headers)=)[^"])+)(?:[?&]ck=([^"&]+))?(?:[?&]headers=([^"&]+))?', response)
        if matches:
            mpd_url = matches[1]
            if matches[2]:
                base64key = matches[2].replace('%3D', '=')
                keys = base64.b64decode(base64key + '=' * (-len(base64key) % 4)).decode('utf-8').replace(';', ',')
                keys = unpackKeys(keys)
                if ',' in keys:
                    keys = hex_to_oct_keys(keys)
            else:
                base64key = None
            if matches[3]:
                headers_dict = json.loads(base64.b64decode(unquote(matches[3]) + '=' * (-len(unquote(matches[3])) % 4)).decode('utf-8'))
            else:
                headers_dict = None
            return mpd_url, keys, headers_dict
    except Exception as e:
        print(f'Error during URL parsing: {e}')
        return None, None, None


def getCurrentDayIT():
    days = {0: "lunedì", 1: "martedì", 2: "mercoledì", 3: "giovedì", 4: "venerdì", 5: "sabato", 6: "domenica"}
    return days[datetime.now().weekday()]


def getEventsDict() -> list[dict]:
    parsed_items = []
    sesh = login_to_site('https://thisnot.business', '2025')
    response = sesh.get('https://thisnot.business/api/eventi.json', headers=headers)
    response.raise_for_status()
    events_dict = response.json()
    current_day = getCurrentDayIT()
    for item in events_dict["eventi"]:
        if item.get("giorno", "").lower() == current_day:
            url, kid_key_pair, headers_dict = parseEventUrl(item["link"], sesh)
            if url is not None:
                parsed_items.append({
                    "title": f'[TN] {item["orario"]} {item["evento"]} ({item["competizione"]})',
                    "manifest_url": url
                })
                if kid_key_pair:
                    parsed_items[-1]["kid_key_pair"] = kid_key_pair
                if headers_dict:
                    parsed_items[-1]["headers"] = headers_dict
    return parsed_items, len(parsed_items)


if __name__ == "__main__":
    events_dict = getEventsDict()
    print(events_dict)
    print(f"✅ Found {len(events_dict[0])} channels from TN.")
