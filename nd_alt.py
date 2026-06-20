import requests
import re
import json
from utils import base64decode

SOURCE_B64 = 'aHR0cHM6Ly9naXRodWIuY29tL0xlaW5hZGYxL2xpc3RhL3Jhdy9yZWZzL2hlYWRzL21haW4vbGlzdGFfcHJpdmF0YS5tM3U='


def process_entry(entry: str) -> dict:
    entry_dict = {}
    entry_dict["group"], entry_dict["tvg_logo"], title = re.search(r'#EXTINF.+group-title="([^"]*)".*tvg-logo="([^"]*)".*,(.+)', entry).groups()
    key = re.search(r'license_key=(.+)', entry)
    if key:
        entry_dict["kid_key_pair"] = key.group(1)
    entry_dict["manifest_url"] = re.search(r'^http[^\s]+', entry, flags=re.MULTILINE).group(0)
    entry_dict["title"] = f'[ND] {title}{" [DAZN]" if "dazn" in entry_dict["manifest_url"] else ""}'
    return entry_dict


def split_m3u_entries(m3u_content: str) -> list[str]:
    """Split M3U content into individual entries"""
    entries = []
    current_entry = []
    lines = m3u_content.split('\n')

    for line in lines:
        if line.startswith('# '):  # Skip comments
            continue
        if line.strip() and not line.startswith('#'):
            current_entry.append(line)
            if current_entry:
                entries.append('\n'.join(current_entry))
                current_entry = []
        elif line.strip():  # Skip empty lines, keep metadata
            current_entry.append(line)
    if current_entry:
        entries.append('\n'.join(current_entry))
    return entries


def filter_entries(entries_list: list[dict]) -> list[dict]:
    filtered_entries = []
    for entry_dict in entries_list:
        if 'dazn' in entry_dict["group"].lower():
            filtered_entries.append(entry_dict)
        del entry_dict["group"]
        del entry_dict["tvg_logo"]
    return filtered_entries


def getNdaChannelsDict() -> list[dict]:
    try:
        response = requests.get(base64decode(SOURCE_B64)).text
        m3u_entries = split_m3u_entries(response)
        processed_entries = [process_entry(entry) for entry in m3u_entries]
        filtered_entries = filter_entries(processed_entries)
    except Exception as e:
        print(f'(nda) {e.__class__.__module__}.{e.__class__.__name__}: {e}')
        return []
    return filtered_entries


if __name__ == "__main__":
    channels_dict = getNdaChannelsDict()
    print(json.dumps(channels_dict, indent=4))
    print(f"✅ Found {len(channels_dict)} channels from ND.")
