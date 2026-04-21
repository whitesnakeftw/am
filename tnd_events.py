import os
import requests
import base64
import re
import json
import traceback
from utils import base64decode, unpackKeys, USER_AGENT, TIME_RE
from dotenv import load_dotenv

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


def getCurrentDayIT(next: int = 0) -> str:
    from datetime import datetime
    days = {0: "lunedì", 1: "martedì", 2: "mercoledì", 3: "giovedì", 4: "venerdì", 5: "sabato", 6: "domenica"}
    return normalize(days[datetime.now().weekday() + next])


def get_channels(response: str) -> list[dict]:
    try:
        channel_data = re.search(r'const\s*(?:_0xD|\bd)ata\s*=\s*(.+?);', response).group(1)
    except AttributeError as e:
        print(f'(tnd) {e.__class__.__module__}.{e.__class__.__name__}: {e}')
        traceback.print_exc()
        return []
    channel_data_dict = json.loads(channel_data)
    matches = re.findall(r'data-l="([^"]+)"\s*data-id="([^"]+)"\s*data-name="([^"]+)"', response)
    matches_dict = {match[1]: {"name": match[2], "category": match[0]} for match in matches}
    channel_data_list = []
    for channel_id, data in channel_data_dict.items():
        if channel_id not in matches_dict:
            continue
        channel_info = matches_dict[channel_id]
        channel_data_list.append({
            "ch_title": channel_info["name"],
            "ch_category": channel_info["category"],
            **data,
        })

    valid_channels = []
    for item in channel_data_list:
        stream_info = base64decode(item["p"])
        try:  # Case DAZN
            manifest, kid_key_pair_b64, headers = re.search(r'(.+?)[\?&]ck=(.+?)&headers=(.+)', stream_info).groups()
            item["headers"] = json.loads(base64decode(headers))
        except AttributeError:
            try:  # Case Now/Wow
                manifest, kid_key_pair_b64 = re.search(r'(.+?)[\?&]ck=(.+)', stream_info).groups()
            except AttributeError:
                continue
        kid_key_pair = base64decode(kid_key_pair_b64)
        item["manifest_url"] = manifest
        item["kid_key_pair"] = unpackKeys(kid_key_pair)
        del item["p"]
        del item["s"]
        valid_channels.append(item)
    return valid_channels


def get_events(response: str) -> list[dict]:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response, "html.parser")
    events = []
    current_day, next_day = getCurrentDayIT(), getCurrentDayIT(next=1)
    for card in soup.select(".event-card"):
        meta = card.select_one(".ev-meta")
        date = meta.find_all("span")[1].get_text(strip=True)
        time_comp = meta.select_one(".ev-ora").get_text(strip=True)
        time = TIME_RE.search(time_comp)[0]

        # Skip event if it's not today after 06:00am, or tomorrow until 11:30am
        if all(normalize(x) not in normalize(date.lower()) for x in (current_day, next_day)):
            continue
        elif normalize(current_day) in normalize(date.lower()):
            if time < "06:00":
                continue
        elif normalize(next_day) in normalize(date.lower()):
            if time > "11:30":
                continue

        title = card.select_one(".ev-title").get_text(strip=True)
        channels_block = card.select_one(".ev-channels")
        lines = [line.strip() for line in channels_block.get_text("\n", strip=True).split("\n") if 'Categoria:' in line]
        for line in lines:
            _, rest = line.split("Categoria:")
            cat, ch = rest.split("- Canale:")
            ch = ch.strip().rsplit(" (", 1)[0]
            events.append({
                "title": f"[TNd] {time} {title} [{ch}]",
                "ev_channel": ch.strip(),
                "ev_category": cat.strip(),
                # "date": date,
            })
    return events


def getTndEventsDict() -> list[dict]:
    try:
        response = requests.get(url, headers=HEADERS).text
    except Exception as e:
        print(f'(tnd) {e.__class__.__module__}.{e.__class__.__name__}: {e}')
        traceback.print_exc()
        return [], 0
    events = get_events(response)
    channels = get_channels(response)
    result = []
    for event in events:
        key = normalize(f'{event["ev_channel"]}-{event["ev_category"]}')
        channel = next((ch for ch in channels if normalize(f'{ch["ch_title"]}-{ch["ch_category"]}') == key), None)
        if channel:
            merged = {**channel, **event}
            for k in ["ev_channel", "ev_category", "ch_title", "ch_category"]:
                del merged[k]
            result.append(merged)
    return result, len(result)


if __name__ == "__main__":
    events_dict, n = getTndEventsDict()
    print(json.dumps(events_dict, indent=4))
    print(f"✅ Found {n} channels from TNd.")
