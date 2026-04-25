import os
import requests
import base64
import re
import json
import traceback
import asyncio
from playwright.async_api import async_playwright
from utils import base64decode, unpackKeys, hex_to_oct_keys, getCurrentDayIT, USER_AGENT, TIME_RE
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
}


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9\+]", "", text.lower())


async def get_response():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=USER_AGENT,
            extra_http_headers=HEADERS,
            viewport={"width": 1920, "height": 879},
        )
        page = await context.new_page()
        await page.goto(url, wait_until="load")
        await page.wait_for_timeout(6000)
        response = await page.content()
        await browser.close()
        return response


def get_channels(response: str) -> list[dict]:
    try:
        channel_data = re.search(r'const\s*(?:_0xD|\bd)ata\s*=\s*(.+?);', response, re.DOTALL).group(1)
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
            "ch_id": channel_id,
            "ch_title": channel_info["name"],
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
        kid_key_pair = unpackKeys(base64decode(kid_key_pair_b64))
        item["manifest_url"] = manifest
        item["kid_key_pair"] = hex_to_oct_keys(kid_key_pair) if ',' in kid_key_pair else kid_key_pair
        del item["p"]
        del item["s"]
        valid_channels.append(item)
    return valid_channels


def get_events(response: str) -> list[dict]:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response, "html.parser")
    events = []
    current_day, next_day = normalize(getCurrentDayIT()), normalize(getCurrentDayIT(next=1))
    for card in soup.select(".event-card"):
        meta = card.select_one(".ev-meta")
        date = meta.find_all("span")[1].get_text(strip=True)
        time_comp = meta.select_one(".ev-ora").get_text(strip=True)
        time = TIME_RE.search(time_comp)[0]

        # Skip event if it's not today after 06:00am, or tomorrow until 11:30am
        n_date = normalize(date.lower())
        if all(normalize(x) not in n_date for x in (current_day, next_day)):
            continue
        elif current_day in n_date:
            if time < "06:00":
                continue
        elif next_day in n_date:
            if time > "11:30":
                continue

        title = card.select_one(".ev-title").get_text(strip=True)
        channels_block = card.select_one(".ev-channels-list")

        for ch_tag in channels_block.select(".agenda-link"):
            ch_name = ch_tag.get_text(strip=True).rsplit(" [", 1)[0]
            ch_id = ch_tag.get("onclick", "").split("'")[1]
            events.append({
                "title": f"[TNd] {time} {title} [{ch_name}]",
                "ev_ch_id": ch_id,
            })
    return events


def getTndEventsDict() -> list[dict]:
    try:
        # response = requests.get(url, headers=HEADERS).text
        response = asyncio.run(get_response())
    except Exception as e:
        print(f'(tnd) {e.__class__.__module__}.{e.__class__.__name__}: {e}')
        traceback.print_exc()
        return [], 0
    events = get_events(response)
    channels = get_channels(response)
    result = []
    for event in events:
        channel = next((ch for ch in channels if ch["ch_id"] == event["ev_ch_id"]), None)
        if channel:
            merged = {**channel, **event}
            for k in ["ch_id", "ch_title", "ev_ch_id"]:
                del merged[k]
            result.append(merged)
    return result, len(result)


if __name__ == "__main__":
    events_dict, n = getTndEventsDict()
    print(json.dumps(events_dict, indent=4))
    print(f"✅ Found {n} events from TNd.")
