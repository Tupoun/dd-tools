"""
Knihovna pro enkódování a dekódování textu
"""

import base64
import urllib.parse


ALGORITHMS = [
    ('base64',    'Base64'),
    ('base64url', 'Base64 URL-safe (JWT/OAuth)'),
    ('base85',    'Base85'),
    ('url',       'URL encode'),
    ('hex',       'Hex'),
]


def encode(text, algorithm):
    try:
        b = text.encode('utf-8')
        if algorithm == 'base64':
            return base64.b64encode(b).decode('ascii'), None
        elif algorithm == 'base64url':
            return base64.urlsafe_b64encode(b).rstrip(b'=').decode('ascii'), None
        elif algorithm == 'base85':
            return base64.b85encode(b).decode('ascii'), None
        elif algorithm == 'url':
            return urllib.parse.quote(text, safe=''), None
        elif algorithm == 'hex':
            return b.hex(' '), None
        return None, f'Neznámý algoritmus: {algorithm}'
    except Exception as e:
        return None, str(e)


def decode(text, algorithm):
    try:
        t = text.strip()
        if algorithm == 'base64':
            return base64.b64decode(t).decode('utf-8'), None
        elif algorithm == 'base64url':
            t += '=' * (-len(t) % 4)
            return base64.urlsafe_b64decode(t).decode('utf-8'), None
        elif algorithm == 'base85':
            return base64.b85decode(t.encode('ascii')).decode('utf-8'), None
        elif algorithm == 'url':
            return urllib.parse.unquote(t), None
        elif algorithm == 'hex':
            return bytes.fromhex(t.replace(' ', '').replace(':', '')).decode('utf-8'), None
        return None, f'Neznámý algoritmus: {algorithm}'
    except Exception as e:
        return None, str(e)
