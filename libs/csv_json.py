"""
Knihovna pro konverzi mezi CSV a JSON
"""

import csv
import json
import io

MAX_INPUT = 1_000_000


def csv_to_json(text, delimiter=','):
    if len(text) > MAX_INPUT:
        return None, 'Vstup je příliš velký (max 1 MB)'
    try:
        reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
        rows = list(reader)
        if not rows:
            return None, 'CSV neobsahuje žádná data'
        return json.dumps(rows, indent=2, ensure_ascii=False), None
    except Exception as e:
        return None, str(e)


def json_to_csv(text, delimiter=','):
    if len(text) > MAX_INPUT:
        return None, 'Vstup je příliš velký (max 1 MB)'
    try:
        data = json.loads(text)
        if not isinstance(data, list):
            return None, 'JSON musí být pole objektů [ {...}, {...} ]'
        if not data:
            return '', None
        if not isinstance(data[0], dict):
            return None, 'JSON musí být pole objektů [ {...}, {...} ]'

        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=data[0].keys(),
            delimiter=delimiter,
            extrasaction='ignore'
        )
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue(), None
    except json.JSONDecodeError as e:
        return None, f'Chyba JSON: {e}'
    except Exception as e:
        return None, str(e)
