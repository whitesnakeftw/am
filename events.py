import am
import x
from sportzx import SportzxClient

OUTFILE = "last_minute.m3u8"


def create_m3u_entry(item: dict) -> str:
    entry = f'#EXTINF:-1 group-title="ULTIMO MINUTO",{item["title"]}'
    if item.get("headers"):
        entry += f"\n#KODIPROP:inputstream.adaptive.stream_headers={item['headers']}"
    if item.get("kid_key_pair"):
        entry += f"\n#KODIPROP:inputstream.adaptive.license_type=clearkey\n#KODIPROP:inputstream.adaptive.license_key={item['kid_key_pair']}"
    entry += f"\n{item['manifest_url']}"
    if item.get("headers"):
        entry += f"?|{item['headers']}"
    return entry


def create_m3u8_playlist(entries: list[dict]) -> str:
    playlist = ''
    for entry in entries:
        playlist += create_m3u_entry(entry) + "\n\n"
    return playlist


def getAmChannels() -> tuple[str, int]:
    channels_dict = am.get_channels_dict()
    filtered_items = am.filter_items(channels_dict)
    am_channels = create_m3u8_playlist(filtered_items)
    return am_channels, len(filtered_items)


def getXChannels() -> tuple[str, int]:
    channels_dict, n = x.getXchannelsDict()
    channels = create_m3u8_playlist(channels_dict)
    return channels, n


def getSportzxChannels() -> tuple[str, int]:
    client = SportzxClient(excluded_categories=["adult", "test", "xxx", "cricket", "icc "])
    channels = client.get_channels()
    if channels:
        sportzx_channels, n_channels = client.generate_m3u(channels=channels, filename="", generic_logo="")
    else:
        print("No channels found from SPORTZX")
    return sportzx_channels, n_channels


am_channels, n_am = getAmChannels()
x_channels, n_x = getXChannels()
sportzx_channels, n_sportzx = getSportzxChannels()

with open(OUTFILE, 'w', encoding='utf-8') as f:
    f.write("#EXTM3U\n\n" + am_channels + x_channels + sportzx_channels)
print(f"✅ Playlist {OUTFILE} created with {n_am}(am)+{n_x}(x)+{n_sportzx}(sportzx) entries.")
