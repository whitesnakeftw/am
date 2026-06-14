import json
import requests
import traceback
from datetime import datetime
from zoneinfo import ZoneInfo
from utils import USER_AGENT, base64decode, fix_time

SOURCE_B64 = 'aHR0cHM6Ly9ub2RybS5vbmxpbmUvbGlzdC9kei5qc29u'


def process_event(event: dict) -> dict:
    extracted_time = datetime.fromisoformat(event.pop("start")).astimezone(ZoneInfo("Europe/Rome")).strftime("%H:%M")
    extracted_time = fix_time(extracted_time, check_dst=False, no_add=True)
    broadcaster = ' [DAZN]' if '.dazn.' in event["mpd"] else ''
    event["title"] = f'[ND] {extracted_time} {event.pop("name")}{broadcaster}'
    event["manifest_url"] = event.pop("mpd")
    event["kid_key_pair"] = event.pop("key")
    # event["logo"] = event.pop("image")
    del event["image"]
    del event["end"]
    return event


def getNdChannelsDict() -> list[dict]:
    try:
        events_dict = requests.get(base64decode(SOURCE_B64), headers={"User-Agent": USER_AGENT}).json()
    except Exception as e:
        print(f'(nd) {e.__class__.__module__}.{e.__class__.__name__}: {e}')
        traceback.print_exc()
        return []
    result = []
    for comp, events in events_dict.items():
        for event in events:
            if 'volley' in comp.lower():
                event["name"] = f'(Volley) {event["name"]}'
            result.append(process_event(event))
    return result


if __name__ == "__main__":
    channels_dict = getNdChannelsDict()
    print(json.dumps(channels_dict, indent=4))
    print(f"✅ Found {len(channels_dict)} channels from ND.")
