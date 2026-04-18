from dotenv import load_dotenv
import os
import requests
import base64
import re
import json
from utils import extract_expiration, base64decode, USER_AGENT, TIME_RE
from tn import unpackKeys

load_dotenv()

url = os.getenv("URL")
user = os.getenv("USER")
password = os.getenv("PASSWORD")

HEADERS = {
    'authorization': f'Basic {base64.b64encode(f"{user}:{password}".encode()).decode()}',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'upgrade-insecure-requests': '1',
    'user-agent': USER_AGENT,
}


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9\+]", "", text.lower())


def getCurrentDayIT() -> str:
    from datetime import datetime
    days = {0: "lunedì", 1: "martedì", 2: "mercoledì", 3: "giovedì", 4: "venerdì", 5: "sabato", 6: "domenica"}
    return normalize(days[datetime.now().weekday()])


def get_channels(response: str) -> list[dict]:
    channel_data = re.search(r'const\s*(?:_0xD|\bd)ata\s*=\s*(.+?);', response).group(1)
    channel_data_dict = json.loads(channel_data)
    matches = re.findall(r'data-l="([^"]+)"\s*data-id="([^"]+)"\s*data-name="([^"]+)"', response)
    matches_dict = {match[1]: {"name": match[2], "category": match[0]} for match in matches}
    channel_data_list = []
    for channel_id, data in channel_data_dict.items():
        if channel_id not in matches_dict:
            continue
        channel_info = matches_dict[channel_id]
        channel_data_list.append({
            "title": channel_info["name"],
            # "category": channel_info["category"],
            **data,
        })

    valid_channels = []
    for item in channel_data_list:
        stream_info = base64decode(item["p"])
        try:  # Case DAZN
            manifest, kid_key_pair_b64, headers = re.search(r'(.+?)[\?&]ck=(.+?)&headers=(.+)', stream_info).groups()
            item["headers"] = json.loads(base64decode(headers))
            item["expiration"] = extract_expiration(item["headers"]["dazn-token"])
        except AttributeError:
            try:  # Case Now/Wow
                manifest, kid_key_pair_b64 = re.search(r'(.+?)[\?&]ck=(.+)', stream_info).groups()
            except AttributeError:
                continue
        kid_key_pair = base64decode(kid_key_pair_b64)
        item["manifest_url"] = manifest
        item["kid_key_pair"] = unpackKeys(kid_key_pair)
        if not item.get("expiration"):
            try:
                item["expiration"] = extract_expiration(item["s"])
            except TypeError:
                pass
        del item["p"]
        del item["s"]
        valid_channels.append(item)
    return valid_channels


def get_events(response: str) -> list[dict]:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response, "html.parser")
    events = []
    current_day = getCurrentDayIT()
    for card in soup.select(".event-card"):
        meta = card.select_one(".ev-meta")
        date = meta.find_all("span")[1].get_text(strip=True)
        if current_day not in normalize(date.lower()):
            break
        time_comp = meta.select_one(".ev-ora").get_text(strip=True)
        time = TIME_RE.search(time_comp)[0]
        title = card.select_one(".ev-title").get_text(strip=True)
        channels_block = card.select_one(".ev-channels")
        lines = [line.strip() for line in channels_block.get_text("\n", strip=True).split("\n") if 'Categoria:' in line]
        for line in lines:
            _, rest = line.split("Categoria:")
            cat, ch = rest.split("- Canale:")
            ch = ch.strip().rsplit(" (", 1)[0]
            events.append({
                "title": f"[TNd] {time} {title} [{ch}]",
                "channel": ch,
                # "date": date,
                # "category": cat,
            })
    return events


def getTndEventsDict() -> list[dict]:
    response = requests.get(url, headers=HEADERS).text
    events = get_events(response)
    channels = get_channels(response)
    result = []
    for event in events:
        key = normalize(event["channel"])
        channel = next((c for c in channels if normalize(c["title"]) == key), None)
        if channel:
            merged = {**channel, **event}
            del merged["channel"]
            result.append(merged)
    return result, len(result)


if __name__ == "__main__":
    events_dict, n = getTndEventsDict()
    print(json.dumps(events_dict, indent=4))
    print(f"✅ Found {n} channels from TNd.")
