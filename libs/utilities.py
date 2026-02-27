"""
Knihovna pro různé utility: Unix timestamp, unescape
"""

import html
import json
import re
from datetime import datetime, timezone


# ── Unix timestamp ────────────────────────────────────────────────────────────

def timestamp_to_datetime(ts):
    try:
        ts = float(ts)
        utc   = datetime.fromtimestamp(ts, tz=timezone.utc)
        local = datetime.fromtimestamp(ts)
        return {'utc': utc, 'local': local}, None
    except Exception as e:
        return None, f'Neplatný timestamp: {e}'


def datetime_to_timestamp(dt_str):
    formats = [
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d',
        '%d.%m.%Y %H:%M:%S',
        '%d.%m.%Y %H:%M',
        '%d.%m.%Y',
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(dt_str.strip(), fmt)
            return int(dt.timestamp()), None
        except ValueError:
            continue
    return None, 'Nepodporovaný formát. Použij např. 2024-01-15 09:30:00 nebo 15.01.2024 09:30:00'


# ── Unescape ──────────────────────────────────────────────────────────────────

def unescape_json_string(text):
    """Odstraní JSON string escaping: \\n → newline, \\" → ", atd."""
    try:
        stripped = text.strip()
        if not (stripped.startswith('"') and stripped.endswith('"')):
            stripped = f'"{stripped}"'
        return json.loads(stripped), None
    except Exception as e:
        return None, f'Chyba: {e}'


def unescape_unicode(text):
    """Převede \\uXXXX sekvence na skutečné znaky: \\u003c → <"""
    try:
        result = re.sub(
            r'\\u([0-9a-fA-F]{4})',
            lambda m: chr(int(m.group(1), 16)),
            text
        )
        return result, None
    except Exception as e:
        return None, f'Chyba: {e}'


# ── HTML entity ────────────────────────────────────────────────────────────────

def encode_html_entities(text):
    """Escapuje HTML znaky: < → &lt;, & → &amp;, atd."""
    try:
        return html.escape(text, quote=True), None
    except Exception as e:
        return None, f'Chyba: {e}'


def decode_html_entities(text):
    """Odescapuje HTML entity: &lt; → <, &amp; → &, atd."""
    try:
        return html.unescape(text), None
    except Exception as e:
        return None, f'Chyba: {e}'
