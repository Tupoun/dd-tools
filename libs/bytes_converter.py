"""
Knihovna pro převod Unicode escape sekvencí na čísla a zpět
"""

import re
import struct


def escapes_to_number(text, divisor=1, byteorder='big'):
    """
    Převede řetězec s \\uXXXX escape sekvencemi na číslo.

    Args:
        text: Řetězec jako '\\u0000\\u00c6'
        divisor: Dělitel výsledku (např. 100 pro měny)
        byteorder: 'big' nebo 'little'

    Returns:
        tuple: (číslo jako float, chybová zpráva nebo None)
    """
    matches = re.findall(r'\\u([0-9a-fA-F]{4})', text)
    if not matches:
        return None, "Nenalezeny žádné \\uXXXX sekvence"

    bytes_list = [int(m, 16) & 0xFF for m in matches]

    if byteorder == 'little':
        bytes_list = bytes_list[::-1]

    value = 0
    for b in bytes_list:
        value = (value << 8) | b

    if divisor and divisor != 0:
        result = value / divisor
    else:
        result = float(value)

    return result, None


def number_to_escapes(value, divisor=1, byte_count=2, byteorder='big'):
    """
    Převede číslo na řetězec s \\uXXXX escape sekvencemi.

    Args:
        value: Číslo (float nebo int)
        divisor: Násobitel (hodnota se vynásobí před převodem)
        byte_count: Počet bajtů výstupu (1, 2, 4, 8)
        byteorder: 'big' nebo 'little'

    Returns:
        tuple: (řetězec escape sekvencí, chybová zpráva nebo None)
    """
    try:
        int_val = round(float(value) * divisor)
    except (ValueError, TypeError):
        return None, "Neplatná číselná hodnota"

    bytes_list = []
    for _ in range(byte_count):
        bytes_list.append(int_val & 0xFF)
        int_val >>= 8

    if byteorder == 'big':
        bytes_list = bytes_list[::-1]

    result = ''.join(f'\\u{b:04x}' for b in bytes_list)
    return result, None
