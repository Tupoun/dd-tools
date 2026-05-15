"""
Knihovna pro generování hashů
"""

import hashlib

MAX_INPUT = 1_000_000


ALGORITHMS = ['MD5', 'SHA-1', 'SHA-256', 'SHA-512']


def compute_all(text):
    if len(text) > MAX_INPUT:
        return {'error': 'Vstup je příliš velký (max 1 MB)'}
    b = text.encode('utf-8')
    return {
        'MD5':     hashlib.md5(b).hexdigest(),
        'SHA-1':   hashlib.sha1(b).hexdigest(),
        'SHA-256': hashlib.sha256(b).hexdigest(),
        'SHA-512': hashlib.sha512(b).hexdigest(),
    }
