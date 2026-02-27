import am
import x
import tn
from sportzx import SportzxClient

OUTFILE = "last_minute.m3u8"


def create_m3u_entry(item: dict) -> str:
    if isinstance(item.get("headers"), dict):
        item["headers"] = '|'.join(f'{k}={v}' for k, v in item["headers"].items())
    item["title"] = item["title"].replace(':', '\N{MODIFIER LETTER COLON}')
    entry = f'#EXTINF:-1 group-title="ULTIMO MINUTO",{item["title"]}'
    if item.get("headers"):
        entry += f"\n#KODIPROP:inputstream.adaptive.stream_headers={item['headers'].replace('|', '&')}"
    if item.get("kid_key_pair"):
        entry += f"\n#KODIPROP:inputstream.adaptive.license_type=clearkey\n#KODIPROP:inputstream.adaptive.license_key={item['kid_key_pair']}"
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


def getXChannels() -> tuple[str, int]:
    channels_dict, n = x.getXEventsDict()
    channels = create_m3u8_playlist(channels_dict)
    return channels, n


def getTnChannels() -> tuple[str, int]:
    events_dict, n = tn.getTnEventsDict()
    channels = create_m3u8_playlist(events_dict)
    return channels, n


def getSportzxChannels() -> tuple[str, int]:
    client = SportzxClient(excluded_categories=["adult", "test", "xxx", "cricket", "icc "])
    channels_dict = client.get_channels()
    if channels_dict:
        channels, n = client.generate_m3u(channels=channels_dict, filename="", generic_logo="")
    else:
        print("No channels found from SPORTZX")
    return channels, n


am_channels, n_am = getAmChannels()
x_channels, n_x = getXChannels()
tn_channels, n_tn = getTnChannels()
sportzx_channels, n_sportzx = getSportzxChannels()

with open(OUTFILE, 'w', encoding='utf-8') as f:
    f.write("#EXTM3U\n\n" + am_channels + x_channels + tn_channels + sportzx_channels)
print(f"✅ Playlist {OUTFILE} created with {n_am}(am) + {n_x}(xe) + {n_tn}(tn) + {n_sportzx}(sportzx) entries.")
