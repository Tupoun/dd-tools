"""
Knihovna pro parsování a generování cron výrazů
"""

from datetime import datetime, timedelta


MONTH_NAMES = {
    1: 'leden', 2: 'únor', 3: 'březen', 4: 'duben',
    5: 'květen', 6: 'červen', 7: 'červenec', 8: 'srpen',
    9: 'září', 10: 'říjen', 11: 'listopad', 12: 'prosinec',
}

WEEKDAY_NAMES = {
    0: 'neděle', 1: 'pondělí', 2: 'úterý', 3: 'středa',
    4: 'čtvrtek', 5: 'pátek', 6: 'sobota', 7: 'neděle',
}

PRESETS = [
    ('* * * * *',    'Každou minutu'),
    ('0 * * * *',    'Každou hodinu'),
    ('0 0 * * *',    'Každý den o půlnoci'),
    ('0 9 * * 1-5',  'Každý pracovní den v 9:00'),
    ('0 9 * * 1',    'Každé pondělí v 9:00'),
    ('*/15 * * * *', 'Každých 15 minut'),
    ('0 */6 * * *',  'Každých 6 hodin'),
    ('0 0 1 * *',    'První den každého měsíce'),
    ('0 0 1 1 *',    'Jednou ročně (1. ledna)'),
    ('30 18 * * 5',  'Každý pátek v 18:30'),
]


def _parse_field(field, min_val, max_val):
    """Zparsuje jedno pole cron výrazu na množinu čísel."""
    values = set()
    for part in field.split(','):
        part = part.strip()
        if part == '*':
            values.update(range(min_val, max_val + 1))
        elif part.startswith('*/'):
            step = int(part[2:])
            values.update(range(min_val, max_val + 1, step))
        elif '/' in part:
            base, step = part.rsplit('/', 1)
            start, end = map(int, base.split('-'))
            values.update(range(start, end + 1, int(step)))
        elif '-' in part:
            start, end = map(int, part.split('-'))
            values.update(range(start, end + 1))
        else:
            v = int(part)
            if min_val <= v <= max_val:
                values.add(v)
    return sorted(values)


def _describe_field(field, names=None):
    parts = []
    for part in field.split(','):
        if part == '*':
            return None
        elif part.startswith('*/'):
            parts.append(f'každých {part[2:]}')
        elif '/' in part:
            base, step = part.rsplit('/', 1)
            start, end = base.split('-')
            if names:
                parts.append(f'{names.get(int(start), start)}–{names.get(int(end), end)} každých {step}')
            else:
                parts.append(f'{start}–{end} každých {step}')
        elif '-' in part:
            start, end = part.split('-')
            if names:
                parts.append(f'{names.get(int(start), start)}–{names.get(int(end), end)}')
            else:
                parts.append(f'{start}–{end}')
        else:
            if names:
                parts.append(names.get(int(part), part))
            else:
                parts.append(part)
    return ', '.join(parts)


def describe(expression):
    """Vrátí lidsky čitelný popis cron výrazu v češtině."""
    parts = expression.strip().split()
    if len(parts) != 5:
        return None, 'Cron výraz musí mít přesně 5 polí: minuta hodina den měsíc den_týdne'

    m_f, h_f, d_f, mo_f, wd_f = parts
    desc = []

    # Čas
    if m_f == '*' and h_f == '*':
        desc.append('každou minutu')
    elif m_f.startswith('*/') and h_f == '*':
        desc.append(f'každých {m_f[2:]} minut')
    elif m_f == '0' and h_f == '*':
        desc.append('každou hodinu (v celou)')
    elif m_f == '0' and h_f == '0':
        desc.append('každý den o půlnoci (00:00)')
    else:
        h_desc = _describe_field(h_f)
        m_desc = _describe_field(m_f)
        if h_desc is None and m_desc is not None:
            desc.append(f'každou hodinu v minutu {m_desc}')
        elif h_desc is not None and m_desc is None:
            desc.append(f'v hodinu {h_desc} (každou minutu)')
        else:
            m_str = m_desc if m_desc else '0'
            h_str = h_desc if h_desc else '*'
            desc.append(f'v {h_str}:{m_str.zfill(2) if m_str.isdigit() else m_str}')

    # Den / den v týdnu
    if d_f != '*' and wd_f != '*':
        d_desc = _describe_field(d_f)
        w_desc = _describe_field(wd_f, WEEKDAY_NAMES)
        desc.append(f'když {d_desc}. den v měsíci NEBO {w_desc}')
    elif d_f != '*':
        d_desc = _describe_field(d_f)
        desc.append(f'{d_desc}. den v měsíci')
    elif wd_f != '*':
        w_desc = _describe_field(wd_f, WEEKDAY_NAMES)
        desc.append(f'v {w_desc}')

    # Měsíc
    if mo_f != '*':
        mo_desc = _describe_field(mo_f, MONTH_NAMES)
        desc.append(f'v měsíci {mo_desc}')

    return ' | '.join(desc), None


def next_runs(expression, count=5):
    """Vrátí seznam příštích N spuštění cron úlohy."""
    parts = expression.strip().split()
    if len(parts) != 5:
        return None, 'Cron výraz musí mít přesně 5 polí'

    try:
        m_f, h_f, d_f, mo_f, wd_f = parts

        minutes  = _parse_field(m_f,  0, 59)
        hours    = _parse_field(h_f,  0, 23)
        days     = _parse_field(d_f,  1, 31)
        months   = _parse_field(mo_f, 1, 12)
        wd_cron  = _parse_field(wd_f, 0, 7)

        # cron 0/7=neděle → Python weekday 6, cron 1=pondělí → Python 0, …
        py_weekdays = {(wd - 1) % 7 for wd in wd_cron}

        has_day = d_f != '*'
        has_wd  = wd_f != '*'

        runs = []
        dt = datetime.now().replace(second=0, microsecond=0) + timedelta(minutes=1)
        limit = dt + timedelta(days=366)

        while len(runs) < count and dt < limit:
            if dt.month in months and dt.hour in hours and dt.minute in minutes:
                if has_day and has_wd:
                    if dt.day in days or dt.weekday() in py_weekdays:
                        runs.append(dt)
                elif has_day:
                    if dt.day in days:
                        runs.append(dt)
                elif has_wd:
                    if dt.weekday() in py_weekdays:
                        runs.append(dt)
                else:
                    runs.append(dt)
            dt += timedelta(minutes=1)

        return runs, None

    except Exception as e:
        return None, f'Chyba: {str(e)}'


def build(minute='*', hour='*', day='*', month='*', weekday='*'):
    """Sestaví cron výraz z jednotlivých polí."""
    return f'{minute} {hour} {day} {month} {weekday}'
