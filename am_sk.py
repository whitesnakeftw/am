import base64
import json
import re
import requests

# ==============================
# CONFIG
# ==============================

DEFAULT_LOGO = "https://skygo.sky.it/etc/designs/skygo/img/sky-logo@2x.png"
OUTPUT_M3U = "sky.m3u8"
TVG_URL = "https://github.com/whitesnakeftw/epg/releases/download/1.0.0/super.guide.xml.gz"

AMSTAFF_URL = "https://test34344.herokuapp.com/filter.php"

PASSWORD = "MandraKodi3"
DEVICE_ID = "2K1WPN"
VERSION = "2.0.0"

USER_AGENT = f"MandraKodi2@@{VERSION}@@{PASSWORD}@@{DEVICE_ID}"

# ==============================
# DATABASE CANALI
# ==============================

CHANNELS_DB = {
    "dazn": {"nome": "DAZN 1", "logo": "https://github.com/tv-logo/tv-logos/blob/main/countries/belgium/dazn-1-be.png", "group": "Sky Sport"},
    "sport24": {"nome": "Sky Sport 24", "logo": "https://pixel.disco.nowtv.it/logo/skychb_35_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Sport"},
    "sportuno": {"nome": "Sky Sport Uno", "logo": "https://pixel.disco.nowtv.it/logo/skychb_23_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Sport"},
    "sportcalcio": {"nome": "Sky Sport Calcio", "logo": "https://pixel.disco.nowtv.it/logo/skychb_209_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Sport"},
    "sporttennis": {"nome": "Sky Sport Tennis", "logo": "https://pixel.disco.nowtv.it/logo/skychb_559_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Sport"},
    "sportarena": {"nome": "Sky Sport Arena", "logo": "https://pixel.disco.nowtv.it/logo/skychb_24_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Sport"},
    "sportbasket": {"nome": "Sky Sport Basket", "logo": "https://pixel.disco.nowtv.it/logo/skychb_764_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Sport"},
    "sportmax": {"nome": "Sky Sport Max", "logo": "https://pixel.disco.nowtv.it/logo/skychb_248_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Sport"},
    "sportf1": {"nome": "Sky Sport F1", "logo": "https://pixel.disco.nowtv.it/logo/skychb_478_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Sport"},
    "sportmotogp": {"nome": "Sky Sport MotoGP", "logo": "https://pixel.disco.nowtv.it/logo/skychb_483_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Sport"},
    "sportgolf": {"nome": "Sky Sport Golf", "logo": "https://pixel.disco.nowtv.it/logo/skychb_768_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Sport"},
    "sportlegend": {"nome": "Sky Sport Legend", "logo": "https://pixel.disco.nowtv.it/logo/skychb_578_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Sport"},
    "sportmix": {"nome": "Sky Sport Mix", "logo": "https://pixel.disco.nowtv.it/logo/skychb_579_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Sport"},
    "sport251": {"nome": "Sky Sport 251", "logo": "https://pixel.disco.nowtv.it/logo/skychb_917_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Sport"},
    "sport252": {"nome": "Sky Sport 252", "logo": "https://pixel.disco.nowtv.it/logo/skychb_951_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Sport"},
    "sport253": {"nome": "Sky Sport 253", "logo": "https://pixel.disco.nowtv.it/logo/skychb_233_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Sport"},
    "sport254": {"nome": "Sky Sport 254", "logo": "https://pixel.disco.nowtv.it/logo/skychb_234_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Sport"},
    "sport255": {"nome": "Sky Sport 255", "logo": "https://pixel.disco.nowtv.it/logo/skychb_910_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Sport"},
    "sport256": {"nome": "Sky Sport 256", "logo": "https://pixel.disco.nowtv.it/logo/skychb_912_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Sport"},
    "sport257": {"nome": "Sky Sport 257", "logo": "https://pixel.disco.nowtv.it/logo/skychb_775_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Sport"},
    "sport258": {"nome": "Sky Sport 258", "logo": "https://pixel.disco.nowtv.it/logo/skychb_912_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Sport"},
    "sport259": {"nome": "Sky Sport 259", "logo": "https://pixel.disco.nowtv.it/logo/skychb_912_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Sport"},

    "tg24": {"nome": "Sky TG24", "logo": "https://pixel.disco.nowtv.it/logo/skychb_519_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Intrattenimento"},
    "uno": {"nome": "Sky Uno", "logo": "https://pixel.disco.nowtv.it/logo/skychb_477_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Intrattenimento"},
    "unoplus": {"nome": "Sky Uno+", "logo": "https://pixel.disco.nowtv.it/logo/skychb_432_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Intrattenimento"},
    "atlantic": {"nome": "Sky Atlantic", "logo": "https://pixel.disco.nowtv.it/logo/skychb_226_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Intrattenimento"},
    "serie": {"nome": "Sky Serie", "logo": "https://pixel.disco.nowtv.it/logo/skychb_684_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Intrattenimento"},
    "investigation": {"nome": "Sky Investigation", "logo": "https://pixel.disco.nowtv.it/logo/skychb_686_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Intrattenimento"},
    "collection": {"nome": "Sky Collection", "logo": "https://images.contentstack.io/v3/assets/blt4b099fa9cc3801a6/blt6210e5c9e5633b2c/69088303a15f04806ab5deed/logo_sky_collection.png", "group": "Sky Intrattenimento"},
    "crime": {"nome": "Sky Crime", "logo": "https://pixel.disco.nowtv.it/logo/skychb_249_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Intrattenimento"},
    "history": {"nome": "History Channel", "logo": "https://pixel.disco.nowtv.it/logo/skychb_513_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Intrattenimento"},
    "documentaries": {"nome": "Sky Documentaries", "logo": "https://pixel.disco.nowtv.it/logo/skychb_697_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Intrattenimento"},
    "adventure": {"nome": "Sky Adventure", "logo": "https://pixel.disco.nowtv.it/logo/skychb_961_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Intrattenimento"},
    "nature": {"nome": "Sky Nature", "logo": "https://pixel.disco.nowtv.it/logo/skychb_695_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Intrattenimento"},
    "arte": {"nome": "Sky Arte", "logo": "https://pixel.disco.nowtv.it/logo/skychb_74_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Intrattenimento"},
    "comedycentral": {"nome": "Comedy Central", "logo": "https://pixel.disco.nowtv.it/logo/skychb_404_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Intrattenimento"},
    "mtv": {"nome": "MTV", "logo": "https://pixel.disco.nowtv.it/logo/skychb_763_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Intrattenimento"},

    "cinemauno": {"nome": "Sky Cinema Uno", "logo": "https://pixel.disco.nowtv.it/logo/skychb_202_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Cinema"},
    "cinemastories": {"nome": "Sky Cinema Stories", "logo": "https://pixel.disco.nowtv.it/logo/skychb_564_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Cinema"},
    "cinemacollection": {"nome": "Sky Cinema Collection", "logo": "https://pixel.disco.nowtv.it/logo/skychb_204_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Cinema"},
    "cinemafamily": {"nome": "Sky Cinema Family", "logo": "https://pixel.disco.nowtv.it/logo/skychb_255_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Cinema"},
    "cinemaaction": {"nome": "Sky Cinema Action", "logo": "https://pixel.disco.nowtv.it/logo/skychb_206_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Cinema"},
    "cinemasuspense": {"nome": "Sky Cinema Suspense", "logo": "https://pixel.disco.nowtv.it/logo/skychb_47_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Cinema"},
    "cinemacomedy": {"nome": "Sky Cinema Comedy", "logo": "https://pixel.disco.nowtv.it/logo/skychb_30_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Cinema"},
    "cinemaromance": {"nome": "Sky Cinema Romance", "logo": "https://pixel.disco.nowtv.it/logo/skychb_231_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Cinema"},
    "cinemadrama": {"nome": "Sky Cinema Drama", "logo": "https://pixel.disco.nowtv.it/logo/skychb_769_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Cinema"},

    "deakids": {"nome": "Deakids", "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/dea-kids-it.png", "group": "Sky Bambini"},
    "nickjr": {"nome": "Nick Junior", "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/nick-jr-it.png", "group": "Sky Bambini"},
    "nickelodeon": {"nome": "Nickelodeon", "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/nickelodeon-it.png", "group": "Sky Bambini"},
    "cartoonnetwork": {"nome": "Cartoon Network", "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/cartoon-network-it.png", "group": "Sky Bambini"},
    "boomerang": {"nome": "Boomerang", "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/boomerang-it.png", "group": "Sky Bambini"},
    "mrbean": {"nome": "Mr Bean Channel", "logo": "https://i.postimg.cc/rmwVGQNn/Mr-Bean-29-logo-svg.png", "group": "Sky Bambini"},
}


# ==============================
# UTILS
# ==============================

def clean_m3u_text(text):
    if not text:
        return text
    text = re.sub(r"\[/?COLOR[^\]]*\]", "", text, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", text).strip()


def normalize(text):
    return re.sub(r"[^a-z0-9\+]", "", text.lower())


def match_channel(title):
    key = normalize(title)
    # iterate channels in order of decreasing key length so more specific keys
    # (e.g. 'unoplus') are tested before shorter, more general ones ('uno')
    for k, v in sorted(CHANNELS_DB.items(), key=lambda item: -len(item[0])):
        if k in key or normalize(v["nome"]) in key:
            return v
    return None

# ==============================
# DECODE AMSTAFF
# ==============================


def decode_amstaff(encoded):
    if encoded.startswith("amstaff@@"):
        encoded = encoded[9:]

    encoded = encoded.strip()
    encoded += "=" * (-len(encoded) % 4)

    try:
        decoded = base64.b64decode(encoded).decode("utf-8")
    except:
        return None

    if "|" not in decoded or ":" not in decoded:
        return None

    url, key_part = decoded.split("|", 1)
    key_id, key = key_part.split(":", 1)

    return url, key_id, key

# ==============================
# FETCH (FIX JSON)
# ==============================


def extract_with_regex(text):
    results = []
    pattern = re.compile(
        r'"title"\s*:\s*"([^"]+)"[\s\S]*?"myresolve"\s*:\s*"([^"]+)"',
        re.IGNORECASE
    )
    for title, myresolve in pattern.findall(text):
        results.append((title, myresolve))
    return results


def fetch_amstaff_channels():
    r = requests.get(
        AMSTAFF_URL,
        headers={"User-Agent": USER_AGENT},
        params={"numTest": "A1A260"},
        timeout=15
    )

    text = r.text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        cleaned = re.sub(r",\s*([}\]])", r"\1", text)
        cleaned = re.sub(r"//.*?$", "", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL)
        try:
            data = json.loads(cleaned)
        except:
            print("⚠️ JSON non valido → uso regex")
            return extract_with_regex(text)

    found = []

    def walk(o):
        if isinstance(o, dict):
            if "title" in o and "myresolve" in o:
                found.append((o["title"], o["myresolve"]))
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for i in o:
                walk(i)

    walk(data)
    return found

# ==============================
# M3U
# ==============================


def generate_m3u(channels):
    m3u = f'#EXTM3U url-tvg="{TVG_URL}"\n\n'

    # Helper to process a single (title, encoded) entry and append it to m3u
    def _process_item(raw_title, encoded_item):
        title = clean_m3u_text(raw_title)

        decoded = decode_amstaff(encoded_item)
        if not decoded:
            print(f"⚠️ decode_amstaff failed for title={repr(title)}")
            return False

        url, key_id, key = decoded
        meta = match_channel(title)

        name = clean_m3u_text(meta["nome"] if meta else title)
        logo = meta["logo"] if meta else DEFAULT_LOGO
        group = meta["group"] if meta else "Altro"
        tvg_id = name.replace(" ", '') + '.it'

        nonlocal m3u
        m3u += f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-logo="{logo}" group-title="{group}",{name}\n'
        m3u += '#KODIPROP:inputstream.adaptive.license_type=clearkey\n'
        m3u += f'#KODIPROP:inputstream.adaptive.license_key={key_id}:{key}\n'
        m3u += f'{url}\n\n'
        return True

    # Make a mutable copy of fetched channels. It will remove items as they are placed
    remaining = list(channels)
    # First, emit channels in the order defined by CHANNELS_DB. For each DB entry,
    # find the first remaining fetched channel that matches it and output it
    for db_key, db_meta in CHANNELS_DB.items():
        found_index = None
        for idx, (title, encoded) in enumerate(remaining):
            matched = match_channel(title)
            # match_channel returns the same dict object from CHANNELS_DB when matched
            if matched is db_meta:
                found_index = idx
                break

        if found_index is not None:
            title, encoded = remaining.pop(found_index)
            _process_item(title, encoded)

    # Append any remaining channels that weren't in CHANNELS_DB or didn't match
    for title, encoded in remaining:
        _process_item(title, encoded)

    with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
        f.write(m3u)

    print(f"✅ File M3U creato: {OUTPUT_M3U}")

# ==============================
# MAIN
# ==============================


if __name__ == "__main__":
    channels = fetch_amstaff_channels()
    generate_m3u(channels)
