import streamlink
from pathlib import Path
import requests
import re


def grab_profile_image(twitch_url):
    response = requests.get(twitch_url).text
    match = re.search(r'<meta\s+name="twitter:image"\s+content="([^"]+)"/>', response)
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


twitch_profiles = [
    "https://www.twitch.tv/grenbaud",
    "https://www.twitch.tv/therealmarzaa",
    "https://www.twitch.tv/gioee",
    "https://www.twitch.tv/kingsleague_it",
    "https://www.twitch.tv/kingsleague",
]

m3u8_file = Path("twitch.m3u8")
user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"
group_title = "TWITCH"
m3u8_content = "#EXTM3U\n"

for profile in twitch_profiles:
    stream_url = get_stream_url(profile)
    if stream_url:
        channel_name = profile.split('/')[-1]
        channel_logo = grab_profile_image(profile)
        m3u8_content += f'#EXTINF:-1 tvg-logo="{channel_logo}" group-title="{group_title}",{channel_name}\n'
        m3u8_content += f"#EXTVLCOPT:http-referrer={profile}\n"
        m3u8_content += f"#EXTVLCOPT:http-origin={profile}\n"
        m3u8_content += f"#EXTVLCOPT:http-user-agent={user_agent}\n"
        m3u8_content += f"{stream_url}\n"
        print(f"ACTIVE stream found for: {profile}")
    else:
        print(f"Channel offline: {profile}")

with open(m3u8_file, "w") as f:
    f.write(m3u8_content)

print(f"M3U8 file created: {m3u8_file}")
