from pathlib import Path
import streamlink
import requests
import re
from utils import USER_AGENT

OUTFILE = Path("twitch.m3u8")
IPHONE_UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"
GROUP_TITLE = "TWITCH"

twitch_profiles = [
    "https://www.twitch.tv/grenbaud",
    "https://www.twitch.tv/therealmarzaa",
    "https://www.twitch.tv/lollolacustre",
    "https://www.twitch.tv/gioee",
    "https://www.twitch.tv/kingsleague_it",
    "https://www.twitch.tv/kingsleague",
    "https://www.twitch.tv/ilrossopiubelloditwitch",
    "https://www.twitch.tv/none_cerbero_podcast",
    "https://www.twitch.tv/naded",
    "https://www.twitch.tv/tylenul",
    "https://www.twitch.tv/halo",
    "https://www.twitch.tv/patrizio_official",
    "https://www.twitch.tv/matteohs",
    "https://www.twitch.tv/marcomerrino",
    "https://www.twitch.tv/ishowspeed",
    "https://www.twitch.tv/andreadel1988",
]


def grab_profile_image(twitch_url):
    response = requests.get(twitch_url, headers={"User-Agent": USER_AGENT}).text
    match = re.search(r'content="([^"]+?-profile_image-[^"]+?)"', response)
    if match:
        return match.group(1)
    return ""


def get_stream_url(twitch_url):
    try:
        streams = streamlink.streams(twitch_url)
        if streams:
            stream = streams["best"]
            return stream.url
        else:
            return None
    except Exception as e:
        print(f"Error {twitch_url}: {e}")
        return None


m3u8_content = "#EXTM3U\n\n"
for profile in twitch_profiles:
    stream_url = get_stream_url(profile)
    if stream_url:
        channel_name = profile.split('/')[-1]
        channel_logo = grab_profile_image(profile)
        m3u8_content += f'#EXTINF:-1 tvg-logo="{channel_logo}" group-title="{GROUP_TITLE}",{channel_name}\n'
        m3u8_content += f"#EXTVLCOPT:http-referrer={profile}\n"
        m3u8_content += f"#EXTVLCOPT:http-origin={profile}\n"
        m3u8_content += f"#EXTVLCOPT:http-user-agent={IPHONE_UA}\n"
        m3u8_content += f"{stream_url}\n\n"
        print(f"ACTIVE stream found for: {profile}")
    else:
        print(f"Channel offline: {profile}")

with open(OUTFILE, "w") as f:
    f.write(m3u8_content)
print(f"✅ Playlist {OUTFILE} created.")
