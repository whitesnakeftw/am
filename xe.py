import requests
import re
from utils import USER_AGENT

SOURCE = R'https://streamvix.hayd.uk/eyJtZWRpYWZsb3dNYXN0ZXIiOmZhbHNlLCJkdnJFbmFibGVkIjpmYWxzZSwiZGlzYWJsZUxpdmVUdiI6ZmFsc2UsInZhdm9vTm9NZnBFbmFibGVkIjp0cnVlLCJ0cmFpbGVyRW5hYmxlZCI6dHJ1ZSwiZGlzYWJsZVZpeHNyYyI6ZmFsc2UsInZpeERpcmVjdCI6ZmFsc2UsInZpeERpcmVjdEZoZCI6ZmFsc2UsImNiMDFFbmFibGVkIjpmYWxzZSwiZ3VhcmRhaGRFbmFibGVkIjp0cnVlLCJndWFyZGFzZXJpZUVuYWJsZWQiOnRydWUsImd1YXJkb3NlcmllRW5hYmxlZCI6dHJ1ZSwiZ3VhcmRhZmxpeEVuYWJsZWQiOnRydWUsImV1cm9zdHJlYW1pbmdFbmFibGVkIjpmYWxzZSwibG9vbmV4RW5hYmxlZCI6ZmFsc2UsInRvb25pdGFsaWFFbmFibGVkIjpmYWxzZSwibG9vbmV4RW5hYmxlZCI6ZmFsc2UsImFuaW1lc2F0dXJuRW5hYmxlZCI6dHJ1ZSwiYW5pbWV3b3JsZEVuYWJsZWQiOnRydWUsImFuaW1ldW5pdHlFbmFibGVkIjp0cnVlLCJhbmltZXVuaXR5QXV0byI6ZmFsc2UsImFuaW1ldW5pdHlGaGQiOmZhbHNlLCJ2aXhQcm94eSI6ZmFsc2UsInZpeFByb3h5RmhkIjp0cnVlfQ==/catalog/tv/streamvix_live/genre=X-Eventi.json'


def clean_title(title: str) -> str:
    title = re.sub(r' {2,}', " ", title)
    title = title.replace('\x8f', '').replace("\N{LARGE RED CIRCLE}", "").strip()
    return title


def extract_keys_from_url(url: str) -> tuple[str, str]:
    kid_key_pair = None
    m = re.search(r'(http.+?)(?:[?&]key_id=([a-f0-9]{32})&key=([a-f0-9]{32}))?$', url, re.IGNORECASE)
    url = m[1]
    if m[2] and m[3]:
        kid_key_pair = f"{m[2]}:{m[3]}"
    return url, kid_key_pair


def extract_time(s: str) -> int:
    match = re.search(r'\b(\d{2})[Hh:](\d{2})\b', s)
    if not match:
        return float("inf")
    hh, mm = match.groups()
    return int(hh) * 60 + int(mm)


def getXeEventsDict() -> tuple[list[dict], int]:
    filtered_channels = []
    try:
        events_dict = requests.get(SOURCE, headers={"User-Agent": USER_AGENT}).json()
        for item in events_dict["metas"]:
            if re.search(r'\b\d{2}[Hh:]\d{2}\b', item["name"]) or 'dazn 1' in item["name"].lower():
                url, kid_key_pair = extract_keys_from_url(item["dynamicDUrls"][0]["url"])
                filtered_channels.append({
                    "title": '[XE] ' + clean_title(item["name"]),
                    "manifest_url": url
                })
                if kid_key_pair:
                    filtered_channels[-1]["kid_key_pair"] = kid_key_pair
    except Exception as e:
        print('Exception:', e)
    sorted_by_time = sorted(filtered_channels, key=lambda x: extract_time(x["title"]))
    return sorted_by_time, len(sorted_by_time)


if __name__ == "__main__":
    channels_dict = getXeEventsDict()
    print(channels_dict)
    print(f"✅ Found {len(channels_dict[0])} channels from X-Eventi.")
