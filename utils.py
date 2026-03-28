import base64
import re

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'
TIME_RE = re.compile(r'\b(\d{2})[Hh:](\d{2})\b')


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
            pairs_list = [item for item in hex_string.split(delim) if item.strip()]  # if item.strip() removes empty arguments
            break
    result = ""
    for item in pairs_list:
        result += '{"kty":"oct","kid":"%s","k":"%s"}' % (*_extract_kid_k(item),)
    oct_keys = '{"keys":[%s]}' % result.replace('}{', '},{')
    return oct_keys
