import re
import json
from tnd_events import get_channels, getTndResponse

TVG_URL = "https://github.com/whitesnakeftw/epg/releases/download/1.0.0/super.guide.xml.gz"

CHANNELS_DB = {
    "dazn": {"nome": "DAZN 1", "logo": "https://github.com/tv-logo/tv-logos/blob/main/countries/belgium/dazn-1-be.png?raw=true", "group": "Sky Sport"},
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
    "history": {"nome": "History", "logo": "https://pixel.disco.nowtv.it/logo/skychb_513_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Intrattenimento"},
    "documentaries": {"nome": "Sky Documentaries", "logo": "https://pixel.disco.nowtv.it/logo/skychb_697_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Intrattenimento"},
    "adventure": {"nome": "Sky Adventure", "logo": "https://pixel.disco.nowtv.it/logo/skychb_961_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Intrattenimento"},
    "nature": {"nome": "Sky Nature", "logo": "https://pixel.disco.nowtv.it/logo/skychb_695_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Intrattenimento"},
    "arte": {"nome": "Sky Arte", "logo": "https://pixel.disco.nowtv.it/logo/skychb_74_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Intrattenimento"},
    "comedycentral": {"nome": "Comedy Central", "logo": "https://pixel.disco.nowtv.it/logo/skychb_404_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Intrattenimento"},
    "mtv": {"nome": "MTV", "logo": "https://pixel.disco.nowtv.it/logo/skychb_763_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Intrattenimento"},

    "cinemauno": {"nome": "Sky Cinema Uno", "logo": "https://pixel.disco.nowtv.it/logo/skychb_202_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Cinema"},
    "cinemadue": {"nome": "Sky Cinema Stories", "logo": "https://pixel.disco.nowtv.it/logo/skychb_564_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Cinema"},
    "cinemastories": {"nome": "Sky Cinema Stories", "logo": "https://pixel.disco.nowtv.it/logo/skychb_564_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Cinema"},
    "cinemacollection": {"nome": "Sky Cinema Collection", "logo": "https://pixel.disco.nowtv.it/logo/skychb_204_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Cinema"},
    "cinemafamily": {"nome": "Sky Cinema Family", "logo": "https://pixel.disco.nowtv.it/logo/skychb_255_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Cinema"},
    "cinemaillumination": {"nome": "Sky Cinema Family", "logo": "https://pixel.disco.nowtv.it/logo/skychb_255_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Cinema"},
    "cinemaaction": {"nome": "Sky Cinema Action", "logo": "https://pixel.disco.nowtv.it/logo/skychb_206_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Cinema"},
    "cinemasuspense": {"nome": "Sky Cinema Suspense", "logo": "https://pixel.disco.nowtv.it/logo/skychb_47_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Cinema"},
    "cinemacomedy": {"nome": "Sky Cinema Comedy", "logo": "https://pixel.disco.nowtv.it/logo/skychb_30_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Cinema"},
    "cinemaromance": {"nome": "Sky Cinema Romance", "logo": "https://pixel.disco.nowtv.it/logo/skychb_231_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Cinema"},
    "cinemadrama": {"nome": "Sky Cinema Drama", "logo": "https://pixel.disco.nowtv.it/logo/skychb_769_lightnow/LOGO_CHANNEL_DARK/4000?language=it-IT&proposition=NOWOTT", "group": "Sky Cinema"},

    "deakids": {"nome": "DeA Kids", "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/dea-kids-it.png", "group": "Sky Bambini"},
    "nickjr": {"nome": "Nick Jr", "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/nick-jr-it.png", "group": "Sky Bambini"},
    "nickelodeon": {"nome": "Nickelodeon", "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/nickelodeon-it.png", "group": "Sky Bambini"},
    "cartoonnetwork": {"nome": "Cartoon Network", "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/cartoon-network-it.png", "group": "Sky Bambini"},
    "boomerang": {"nome": "Boomerang", "logo": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/boomerang-it.png", "group": "Sky Bambini"},
}


def sort_channels_by_db_order(channels: list[dict]) -> list[dict]:
    order_index = {key: index for index, key in enumerate(CHANNELS_DB)}

    def _normalize_channel_key(name: str) -> str:
        return re.sub(r'[^a-z0-9]', '', name.lower())

    def _find_matching_db_key(normalized_name: str) -> str | None:
        if normalized_name in order_index:
            return normalized_name
        candidates = [key for key in order_index if normalized_name.endswith(key) or normalized_name.startswith(key)]
        if not candidates:
            return None
        return max(candidates, key=len)

    ordered_items = []
    unknown_items = []
    for data in channels:
        normalized_name = _normalize_channel_key(data["title"])
        db_key = _find_matching_db_key(normalized_name)
        if db_key is not None:
            db_info = CHANNELS_DB[db_key]
            display_name = db_info.get("nome", data["title"])
            data["category"] = db_info.get("group", "") + " (TNd)"  # Overwrite category from data with category from DB
            data["logo"] = db_info.get("logo", "")
            data["tvg_id"] = display_name.replace(" ", "") + ".it"
            ordered_items.append((order_index[db_key], display_name, data))
        else:
            unknown_items.append((data["title"], data))
    ordered_items.sort(key=lambda item: item[0])
    sorted_items = [(display_name, data) for _, display_name, data in ordered_items] + unknown_items
    return [data for display_name, data in sorted_items]


def filter_and_sort_channels(channels: list[dict]) -> tuple[list[dict], int]:
    for ch in channels:
        ch["title"] = ch.pop("ch_title")
        ch["category"] = ch.pop("ch_category")
        del ch["ch_id"]
    filtered_channels = []
    for channel in channels:
        if channel["category"] != 'Sky Italia':
            continue
        filtered_channels.append(channel)
    sorted_channels = sort_channels_by_db_order(filtered_channels)
    return sorted_channels, len(sorted_channels)


def getTndChannelsDict(response: str) -> tuple[list[dict], int]:
    channel_data, n_channels = filter_and_sort_channels(get_channels(response))
    return channel_data, n_channels


if __name__ == "__main__":
    tnd_response = getTndResponse()
    channels_dict, n_channels = getTndChannelsDict(tnd_response)
    print(json.dumps(channels_dict, indent=4))
    print(f"✅ Found {n_channels} channels from TNd_sk.")
