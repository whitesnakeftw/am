import base64
import re
from datetime import datetime, timezone

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36'
TIME_RE = re.compile(r'\b(\d{2})[Hh:](\d{2})\b')
TIMES_DICT = {
    '00:12': '01:30',
    '00:42': '02:00',
    '01:12': '02:30',
    '01:31': '03:00',
    '01:42': '03:00',
    '02:12': '03:30',
    '02:31': '03:00',
    '02:42': '03:00',
    '03:42': '05:00',
    '04:42': '06:00',
    '05:42': '06:00',
    '09:26': '12:00',
    '10:41': '12:00',
    '10:56': '12:30',
    '11:11': '12:30',
    '12:41': '15:00',
    '13:11': '15:00',
    '13:25': '15:00',
    '13:26': '15:00',
    '13:41': '15:00',
    '15:56': '18:00',
    '16:11': '18:00',
    '16:26': '18:00',
    '16:41': '18:00',
    '16:42': '18:00',
    '16:55': '17:00',
    '16:56': '18:30',
    '16:57': '18:30',
    '17:42': '19:00',
    '17:52': '21:00',
    '18:11': '20:45',
    '18:22': '21:00',
    '18:26': '20:45',
    '18:41': '20:45',
    '18:42': '20:45',
    '18:52': '21:00',
    '18:56': '20:45',
    '19:11': '20:45',
    '19:26': '20:45',
    '19:42': '21:00',
    '19:52': '21:00',
    '20:42': '22:00',
    '20:52': '23:00',
    '21:42': '23:00',
    '22:42': '00:00',
    '23:42': '01:00',
}


def fix_time(title_with_time: str, check_dst: bool = True, no_add: bool = False) -> str:
    def _is_dst() -> bool:
        from datetime import datetime, timedelta
        from zoneinfo import ZoneInfo

        now = datetime.now(ZoneInfo('Europe/Rome'))
        is_dst = now.dst() != timedelta(0)
        return True if is_dst else False

    # def _add_hours_in_secs(hh: str, mm: str, secs_to_add: int) -> tuple[str, str]:
    #     secs = (int(hh) * 3600 + int(mm) * 60) + secs_to_add
    #     return f'{secs // 3600}', f'{(secs % 3600) // 60:02d}'

    try:
        hours, minutes = map(int, TIME_RE.search(title_with_time).groups())
        if check_dst and _is_dst():
            hours = (hours + 1) % 24
        time_str = f'{hours:02d}:{minutes:02d}'
        if time_str in TIMES_DICT.keys():
            hours, minutes = map(int, TIMES_DICT[time_str].split(':'))
        elif not no_add:
            hours = (hours + 1) % 24
    except AttributeError:
        return title_with_time
    return TIME_RE.sub(f'{hours % 24:02d}:{minutes:02d}', title_with_time)


def base64decode(data: str | bytes) -> str:
    from urllib.parse import unquote
    clean_data = unquote(data)
    return base64.b64decode(clean_data + '=' * (-len(clean_data) % 4)).decode('utf-8')


def extract_time(s: str) -> int:
    match = TIME_RE.search(s)
    if not match:
        return 0  # float("inf")
    hh, mm = match.groups()
    return int(hh) * 60 + int(mm)


def getCurrentDayIT(next: int = 0) -> str:
    days = {
        0: "lunedì", 1: "martedì", 2: "mercoledì", 3: "giovedì", 4: "venerdì", 5: "sabato", 6: "domenica"
    }
    return days[(datetime.now().weekday() + next) % 7]


def unpackKeys(keys: str) -> str:
    import json
    try:
        keys = ','.join(f'{kid}:{key}' for kid, key in json.loads(keys).items())
    except json.JSONDecodeError:
        pass
    return keys


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


def time_until_expiry(expiry_timestamp: int) -> str:
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


def extract_expiration(input: str) -> str:
    import jwt
    from zoneinfo import ZoneInfo
    expiration = None
    match_jwt = re.search(r'\beyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b', input, re.MULTILINE)
    if match_jwt:
        token = match_jwt[0]
        expiration = jwt.decode(token, options={"verify_signature": False}).get('exp')
    else:
        match_expiration = re.search(r'(?<!\d)(?<!st%3D)(17\d{8})(?!\d)', input)
        if match_expiration:
            expiration = int(match_expiration[1])
    if expiration:
        human_readable_exp = datetime.fromtimestamp(expiration, tz=timezone.utc).astimezone(ZoneInfo("Europe/Rome")).strftime('%Y-%m-%d %H:%M:%S')
        return f'{human_readable_exp} ({time_until_expiry(expiration)})'
    return ''
