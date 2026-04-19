"""
Knihovna pro různé utility: Unix timestamp, unescape
"""

import html
import json
import re
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


# ── Unix timestamp ────────────────────────────────────────────────────────────

def timestamp_to_datetime(ts, unit='s'):
    try:
        ts = float(ts)
        if unit == 'ms':
            ts = ts / 1_000
        elif unit == 'us':
            ts = ts / 1_000_000
        utc   = datetime.fromtimestamp(ts, tz=timezone.utc)
        local = datetime.fromtimestamp(ts)
        return {'utc': utc, 'local': local}, None
    except Exception as e:
        return None, f'Neplatný timestamp: {e}'


def datetime_to_timestamp(dt_str, unit='s', timezone_name='UTC'):
    try:
        tz = ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, Exception):
        tz = timezone.utc
        timezone_name = 'UTC'

    formats = [
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d',
        '%d.%m.%Y %H:%M:%S',
        '%d.%m.%Y %H:%M',
        '%d.%m.%Y',
    ]

    if not dt_str or not dt_str.strip():
        dt = datetime.now(tz=tz)
    else:
        dt = None
        for fmt in formats:
            try:
                dt = datetime.strptime(dt_str.strip(), fmt).replace(tzinfo=tz)
                break
            except ValueError:
                continue
        if dt is None:
            return None, 'Nepodporovaný formát. Použij např. 2024-01-15 09:30:00 nebo 15.01.2024 09:30:00'

    ts = dt.timestamp()
    if unit == 'ms':
        value = int(ts * 1_000)
    elif unit == 'us':
        value = int(ts * 1_000_000)
    else:
        value = int(ts)

    return {'value': value, 'unit': unit, 'timezone': timezone_name}, None


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


# ── Epoch days ───────────────────────────────────────────────────────────────

EPOCH = date(1970, 1, 1)

def days_since_epoch(date_str=None):
    """Vrátí počet dní od Unix epoch (1970-01-01) k zadanému nebo aktuálnímu datu."""
    try:
        if date_str and date_str.strip():
            target = datetime.strptime(date_str.strip(), '%Y/%m/%d').date()
        else:
            target = date.today()
        days = (target - EPOCH).days
        return {'days': days, 'date': target}, None
    except ValueError:
        return None, 'Neplatný formát data. Použij YYYY/MM/DD, např. 2024/01/15'
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
