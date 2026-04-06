import requests
import re
import json
import base64
import html
import traceback
from datetime import datetime
from urllib.parse import unquote
from utils import hex_to_oct_keys, USER_AGENT

BASE_URL_B64 = 'aHR0cHM6Ly90aGl' + 'zbm90LmJ1c2luZXNz'
BASE_URL = base64.b64decode(BASE_URL_B64).decode("utf-8")

headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9,it;q=0.8,hu;q=0.7',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': f'{BASE_URL}/eventi.php',
    'user-agent': USER_AGENT,
}


def siteLogin(url, password):
    try:
        session = requests.Session()
        response = session.post(url, data={'password': password}, headers={'User-Agent': headers["user-agent"]})
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
        response = session.get(url, headers={'User-Agent': headers["user-agent"]}).text
    except requests.exceptions.MissingSchema:
        try:
            response = session.get(BASE_URL + url, headers={'User-Agent': headers["user-agent"]}).text
        except Exception as e:
            print(f'(tn) {e.__class__.__module__}.{e.__class__.__name__}: {e}')
            traceback.print_exc()
    try:
        response = html.unescape(response)
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
        print(f'(tn) {e.__class__.__module__}.{e.__class__.__name__}: {e}')
        traceback.print_exc()
        return None, None, None


def getCurrentDayIT():
    days = {0: "lunedì", 1: "martedì", 2: "mercoledì", 3: "giovedì", 4: "venerdì", 5: "sabato", 6: "domenica"}
    return days[datetime.now().weekday()]


def getTnEventsDict() -> list[dict]:
    parsed_items = []
    sesh = siteLogin(BASE_URL, '2025')
    try:
        response = sesh.get(f'{BASE_URL}/api/eventi.json', headers=headers)
        events_dict = response.json()
        current_day = getCurrentDayIT()
        today_events = [item for item in events_dict["eventi"] if item.get("giorno", "").lower() == current_day]
        if not today_events:
            today_events = [item for item in events_dict["eventi"] if item.get("giorno", "").lower() == ""]
        for item in today_events:
            url, kid_key_pair, headers_dict = parseEventUrl(item["link"], sesh)
            if url is not None:
                parsed_items.append({
                    "title": f'[TN] {item["orario"]} {item["evento"]} ({item["competizione"]}) [{html.unescape(item["canale"])}]',
                    "manifest_url": url
                })
                if kid_key_pair:
                    parsed_items[-1]["kid_key_pair"] = kid_key_pair
                if headers_dict:
                    parsed_items[-1]["headers"] = headers_dict
    except Exception as e:
        print(f'(tn) {e.__class__.__module__}.{e.__class__.__name__}: {e}')
        traceback.print_exc()
    return parsed_items, len(parsed_items)


if __name__ == "__main__":
    events_dict = getTnEventsDict()
    print(json.dumps(events_dict, indent=4))
    print(f"✅ Found {len(events_dict[0])} channels from TN.")
