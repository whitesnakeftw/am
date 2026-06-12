import re
import am
import nd
import xe
import tn
import tnd_events
import tnd_sk
from sportzx import SportzxClient
from utils import extract_expiration

OUTFILE = "last_minute.m3u8"


def create_m3u_entry(item: dict) -> str:
    if isinstance(item.get("headers"), dict):
        item["headers"] = '|'.join(f'{k}={v}' for k, v in item["headers"].items())
    title = item["title"].replace(':', '\N{MODIFIER LETTER COLON}')
    title = re.sub(r' {2,}', " ", title)
    tvg_id = f' tvg-id="{item.get("tvg_id", "")}"' if item.get("tvg_id") else ''
    logo = f' tvg-logo="{item.get("logo", "")}"' if item.get("logo") else ''
    category = f' group-title="{item.get("category", "ULTIMO MINUTO")}"'
    expiration = extract_expiration(item.get("manifest_url", "") + item.get("headers", ""))

    entry = f'#EXTINF:-1{category}{tvg_id}{logo},{title}'
    if item.get("headers"):
        entry += f"\n#KODIPROP:inputstream.adaptive.stream_headers={item['headers'].replace('|', '&')}"
    if item.get("kid_key_pair"):
        entry += f"\n#KODIPROP:inputstream.adaptive.license_type=clearkey\n#KODIPROP:inputstream.adaptive.license_key={item['kid_key_pair']}"
    if expiration:
        entry += f"\n# Expiration: {expiration}"
    entry += f"\n{item['manifest_url']}"
    if item.get("headers"):
        entry += f"{'&' if '?' in item['manifest_url'] else '?'}|{item['headers']}"
    return entry


def create_m3u8_playlist(entries: list[dict]) -> str:
    playlist = ''
    for entry in entries:
        playlist += create_m3u_entry(entry) + "\n\n"
    return playlist


def getAmChannels() -> tuple[str, int]:
    channels_dict = am.getAmChannelsDict()
    filtered_items = am.filter_items(channels_dict)
    channels = create_m3u8_playlist(filtered_items)
    n = len(filtered_items)
    return channels, n


def getNdChannels() -> tuple[str, int]:
    channels_dict = nd.getNdChannelsDict()
    channels = create_m3u8_playlist(channels_dict)
    n = len(channels_dict)
    return channels, n


def getXeChannels() -> tuple[str, int]:
    channels_dict, n = xe.getXeEventsDict()
    channels = create_m3u8_playlist(channels_dict)
    return channels, n


def getTnChannels() -> tuple[str, int]:
    events_dict, n = tn.getTnEventsDict()
    channels = create_m3u8_playlist(events_dict)
    return channels, n


def getTndChannels(response: str) -> tuple[str, int]:
    events_dict, n = tnd_events.getTndEventsDict(response)
    channels = create_m3u8_playlist(events_dict)
    return channels, n


def getTndSkChannels(response: str) -> tuple[str, int]:
    channels_dict, n = tnd_sk.getTndChannelsDict(response)
    channels = create_m3u8_playlist(channels_dict)
    return channels, n


def getSportzxChannels() -> tuple[str, int]:
    client = SportzxClient(excluded_categories=["adult", "test", "xxx", "cricket", "icc ", "isl", "psl", "indian pr", "f1", "motogp", "wwe"])
    channels_dict = client.get_channels()
    if channels_dict:
        channels, n = client.generate_m3u(channels=channels_dict, filename="", generic_logo="")
    else:
        channels, n = "", 0
        print("No channels found from SPORTZX")
    return channels, n


def build_playlist_from_services(services: list[tuple[str, callable]]) -> tuple[str, list[tuple[str, int]]]:
    playlist_parts = []
    counts = []
    for name, getter in services:
        channels, n = getter()
        playlist_parts.append(channels)
        counts.append((name, n))
    return ''.join(playlist_parts), counts


if __name__ == "__main__":
    tnd_response = tnd_events.getTndResponse()
    services = [
        ("am", getAmChannels),
        ("nd", getNdChannels),
        ("xe", getXeChannels),
        # ("tn", getTnChannels),
        ("tnd", lambda: getTndChannels(tnd_response)),
        ("sportzx", getSportzxChannels),
        ("tnd_sk", lambda: getTndSkChannels(tnd_response)),
    ]

    playlist, counts = build_playlist_from_services(services)
    with open(OUTFILE, 'w', encoding='utf-8') as f:
        f.write(f'#EXTM3U url-tvg="{tnd_sk.TVG_URL}"\n\n{playlist}')
    print(f"✅ Playlist {OUTFILE} created with {' + '.join(f'{n}({name})' for name, n in counts)} entries.")
