import requests
import re
import base64
import json
import traceback
from utils import USER_AGENT, TIME_RE, extract_time

SOURCE_B64 = R'aHR0cHM6Ly9zdHJlYW12aXguaGF5ZC51ay9leUp0WldScFlXWnNiM2ROWVhOMFpYSWlPbVpoYkhObExDSmtkbkpGYm1GaWJHVmtJanBtWVd4elpTd2laR2x6WVdKc1pVeHBkbVZVZGlJNlptRnNjMlVzSW5aaGRtOXZUbTlOWm5CRmJtRmliR1ZrSWpwMGNuVmxMQ0owY21GcGJHVnlSVzVoWW14bFpDSTZkSEoxWlN3aVpHbHpZV0pzWlZacGVITnlZeUk2Wm1Gc2MyVXNJblpwZUVScGNtVmpkQ0k2Wm1Gc2MyVXNJblpwZUVScGNtVmpkRVpvWkNJNlptRnNjMlVzSW1OaU1ERkZibUZpYkdWa0lqcG1ZV3h6WlN3aVozVmhjbVJoYUdSRmJtRmliR1ZrSWpwMGNuVmxMQ0puZFdGeVpHRnpaWEpwWlVWdVlXSnNaV1FpT25SeWRXVXNJbWQxWVhKa2IzTmxjbWxsUlc1aFlteGxaQ0k2ZEhKMVpTd2laM1ZoY21SaFpteHBlRVZ1WVdKc1pXUWlPblJ5ZFdVc0ltVjFjbTl6ZEhKbFlXMXBibWRGYm1GaWJHVmtJanBtWVd4elpTd2liRzl2Ym1WNFJXNWhZbXhsWkNJNlptRnNjMlVzSW5SdmIyNXBkR0ZzYVdGRmJtRmliR1ZrSWpwbVlXeHpaU3dpYkc5dmJtVjRSVzVoWW14bFpDSTZabUZzYzJVc0ltRnVhVzFsYzJGMGRYSnVSVzVoWW14bFpDSTZkSEoxWlN3aVlXNXBiV1YzYjNKc1pFVnVZV0pzWldRaU9uUnlkV1VzSW1GdWFXMWxkVzVwZEhsRmJtRmliR1ZrSWpwMGNuVmxMQ0poYm1sdFpYVnVhWFI1UVhWMGJ5STZabUZzYzJVc0ltRnVhVzFsZFc1cGRIbEdhR1FpT21aaGJITmxMQ0oyYVhoUWNtOTRlU0k2Wm1Gc2MyVXNJblpwZUZCeWIzaDVSbWhrSWpwMGNuVmxmUT09L2NhdGFsb2cvdHYvc3RyZWFtdml4X2xpdmUvZ2VucmU9WC1FdmVudGkuanNvbg=='
SOURCE = base64.b64decode(SOURCE_B64).decode("utf-8")


def clean_title(title: str) -> str:
    title = title.replace('\x8f', '').replace("\N{LARGE RED CIRCLE}", "").strip()
    return title


def extract_keys_from_url(url: str) -> tuple[str, str]:
    kid_key_pair = None
    m = re.search(r'(http.+?)(?:[?&]key_id=([a-f0-9]{32})&key=([a-f0-9]{32}))?$', url, re.IGNORECASE)
    url = m[1]
    if m[2] and m[3]:
        kid_key_pair = f"{m[2]}:{m[3]}"
    return url, kid_key_pair


def getXeEventsDict() -> tuple[list[dict], int]:
    filtered_channels = []
    try:
        events_dict = requests.get(SOURCE, headers={"User-Agent": USER_AGENT}, timeout=15).json()
        for item in events_dict["metas"]:
            if (TIME_RE.search(item["name"]) or 'dazn 1' in item["name"].lower()) and 'secure_stream' not in item["dynamicDUrls"][0]["url"]:
                url, kid_key_pair = extract_keys_from_url(item["dynamicDUrls"][0]["url"])
                filtered_channels.append({
                    "title": '[XE] ' + clean_title(item["name"]),
                    "manifest_url": url
                })
                if kid_key_pair:
                    filtered_channels[-1]["kid_key_pair"] = kid_key_pair
    except Exception as e:
        print(f'(xe) {e.__class__.__module__}.{e.__class__.__name__}: {e}')
        traceback.print_exc()
    sorted_by_time = sorted(filtered_channels, key=lambda x: extract_time(x["title"]))
    return sorted_by_time, len(sorted_by_time)


if __name__ == "__main__":
    channels_dict = getXeEventsDict()
    print(json.dumps(channels_dict, indent=4))
    print(f"✅ Found {len(channels_dict[0])} channels from XE.")
