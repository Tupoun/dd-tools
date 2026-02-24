"""
Knihovna pro dekódování JWT tokenů
"""

import base64
import json
from datetime import datetime


def decode(token):
    parts = token.strip().split('.')
    if len(parts) != 3:
        return None, 'Neplatný JWT token — musí mít 3 části oddělené tečkou.'

    try:
        def b64url_decode(s):
            s += '=' * (-len(s) % 4)
            return base64.urlsafe_b64decode(s)

        header = json.loads(b64url_decode(parts[0]))
        payload = json.loads(b64url_decode(parts[1]))
        signature = parts[2]

        expiry = None
        expired = None
        if 'exp' in payload:
            expiry = datetime.fromtimestamp(payload['exp'])
            expired = expiry < datetime.now()

        return {
            'header': json.dumps(header, indent=2, ensure_ascii=False),
            'payload': json.dumps(payload, indent=2, ensure_ascii=False),
            'signature': signature,
            'expiry': expiry,
            'expired': expired,
        }, None

    except Exception as e:
        return None, f'Chyba při dekódování: {str(e)}'
