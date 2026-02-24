"""
Knihovna pro generování UUID
"""

import uuid

VERSIONS = [
    ('4', 'UUID v4 (náhodný)'),
    ('1', 'UUID v1 (časový)'),
]


def generate(version='4', count=1):
    try:
        count = max(1, min(int(count), 50))
        version = int(version)
        results = []
        for _ in range(count):
            if version == 1:
                results.append(str(uuid.uuid1()))
            else:
                results.append(str(uuid.uuid4()))
        return results, None
    except Exception as e:
        return None, str(e)
