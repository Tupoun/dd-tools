"""
Knihovna pro formátování JSON a XML
"""

import json
import xml.dom.minidom


def format_json(text, sort_keys=False):
    try:
        data = json.loads(text)
        return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=sort_keys), None
    except json.JSONDecodeError as e:
        return None, f'Chyba JSON na řádku {e.lineno}, sloupci {e.colno}: {e.msg}'


def minify_json(text):
    try:
        data = json.loads(text)
        return json.dumps(data, separators=(',', ':'), ensure_ascii=False), None
    except json.JSONDecodeError as e:
        return None, f'Chyba JSON na řádku {e.lineno}, sloupci {e.colno}: {e.msg}'


def format_xml(text):
    try:
        dom = xml.dom.minidom.parseString(text.strip().encode('utf-8'))
        pretty = dom.toprettyxml(indent='  ')
        # Odstraň prázdné řádky, které minidom někdy přidává
        lines = [line for line in pretty.splitlines() if line.strip()]
        return '\n'.join(lines), None
    except Exception as e:
        return None, f'Chyba XML: {e}'
