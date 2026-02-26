import requests
import re

SOURCE = R'https://streamvix.hayd.uk/eyJtZWRpYWZsb3dNYXN0ZXIiOmZhbHNlLCJkdnJFbmFibGVkIjpmYWxzZSwiZGlzYWJsZUxpdmVUdiI6ZmFsc2UsInZhdm9vTm9NZnBFbmFibGVkIjp0cnVlLCJ0cmFpbGVyRW5hYmxlZCI6dHJ1ZSwiZGlzYWJsZVZpeHNyYyI6ZmFsc2UsInZpeERpcmVjdCI6ZmFsc2UsInZpeERpcmVjdEZoZCI6ZmFsc2UsImNiMDFFbmFibGVkIjpmYWxzZSwiZ3VhcmRhaGRFbmFibGVkIjp0cnVlLCJndWFyZGFzZXJpZUVuYWJsZWQiOnRydWUsImd1YXJkb3NlcmllRW5hYmxlZCI6dHJ1ZSwiZ3VhcmRhZmxpeEVuYWJsZWQiOnRydWUsImV1cm9zdHJlYW1pbmdFbmFibGVkIjpmYWxzZSwibG9vbmV4RW5hYmxlZCI6ZmFsc2UsInRvb25pdGFsaWFFbmFibGVkIjpmYWxzZSwibG9vbmV4RW5hYmxlZCI6ZmFsc2UsImFuaW1lc2F0dXJuRW5hYmxlZCI6dHJ1ZSwiYW5pbWV3b3JsZEVuYWJsZWQiOnRydWUsImFuaW1ldW5pdHlFbmFibGVkIjp0cnVlLCJhbmltZXVuaXR5QXV0byI6ZmFsc2UsImFuaW1ldW5pdHlGaGQiOmZhbHNlLCJ2aXhQcm94eSI6ZmFsc2UsInZpeFByb3h5RmhkIjp0cnVlfQ==/catalog/tv/streamvix_live/genre=X-Eventi.json'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'


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


def getXchannelsDict() -> tuple[list[dict], int]:
    events_dict = requests.get(SOURCE, headers={"User-Agent": USER_AGENT}).json()
    filtered_channels = []
    for item in events_dict["metas"]:
        if re.search(r'\b\d{2}H\d{2}\b', item["name"]) or 'dazn 1' in item["name"].lower():
            url, kid_key_pair = extract_keys_from_url(item["dynamicDUrls"][0]["url"])
            filtered_channels.append({
                "title": '[X] ' + clean_title(item["name"]),
                "manifest_url": url
            })
            if kid_key_pair:
                filtered_channels[-1]["kid_key_pair"] = kid_key_pair
    return filtered_channels, len(filtered_channels)


if __name__ == "__main__":
    channels_dict = getXchannelsDict()
    print(channels_dict)
    print(f"✅ Found {len(channels_dict[0])} channels from X-Eventi.")
