import base64
import re
from datetime import datetime, timezone

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36'
TIME_RE = re.compile(r'\b(\d{2})[Hh:](\d{2})\b')


def base64decode(data) -> str:
    from urllib.parse import unquote
    clean_data = unquote(data)
    return base64.b64decode(clean_data + '=' * (-len(clean_data) % 4)).decode('utf-8')


def extract_time(s: str) -> int:
    match = TIME_RE.search(s)
    if not match:
        return 0  # float("inf")
    hh, mm = match.groups()
    return int(hh) * 60 + int(mm)


def hex_to_oct_keys(hex_string: str) -> str:
    def _hex_to_base64url(hex_str: str) -> str:
        decoded_bytes = bytes.fromhex(hex_str)  # Convert hex string to bytes
        base64url_str = base64.urlsafe_b64encode(decoded_bytes).decode('utf-8')  # Encode bytes to Base64URL
        base64url_str = base64url_str.rstrip('=')  # Remove any padding ('=') characters
        return base64url_str

    def _extract_kid_k(kid_key_pair: str) -> tuple[str, str]:
        kid_key_pair = kid_key_pair.replace('{', '').replace('}', '').replace(',', '').replace('"', '').replace("'", "").replace('-', '')
        kid = _hex_to_base64url(kid_key_pair.split(':')[0])
        key = _hex_to_base64url(kid_key_pair.split(':')[1])
        return kid, key

    for delim in (',', ' '):
        if delim in hex_string:
            pairs_list = [item for item in hex_string.split(delim) if item.strip()]  # 'if item.strip()' removes empty arguments stemming from ' ' as delim
            break
    result = ""
    for item in pairs_list:
        result += '{"kty":"oct","kid":"%s","k":"%s"}' % (*_extract_kid_k(item),)
    oct_keys = '{"keys":[%s]}' % result.replace('}{', '},{')
    return oct_keys


def time_until_expiry(expiry_timestamp):
    delta = datetime.fromtimestamp(expiry_timestamp) - datetime.now()
    if delta.total_seconds() <= 0:
        return "already expired"
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if not parts:  # If all are zero (e.g., < 1 minute left)
        parts.append("less than a minute")
    return "in " + " and ".join(parts)


def extract_expiration(input: str):
    import jwt
    from zoneinfo import ZoneInfo
    expiration = None
    match_jwt = re.search(r'\beyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b', input, re.MULTILINE)
    if match_jwt:
        token = match_jwt[0]
        expiration = jwt.decode(token, options={"verify_signature": False}).get('exp')
    else:
        match_expiration = re.search(r'(?<!\d)(17\d{8})(?!\d)', input)
        if match_expiration:
            expiration = int(match_expiration[1])
    if expiration:
        human_readable_exp = datetime.fromtimestamp(expiration, tz=timezone.utc).astimezone(ZoneInfo("Europe/Rome")).strftime('%Y-%m-%d %H:%M:%S')
        return f'{human_readable_exp} ({time_until_expiry(expiration)})'
    return ''
