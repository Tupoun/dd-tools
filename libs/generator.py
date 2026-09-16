"""
Generátor testovacích dat: čísla účtů dle ČNB, rodná čísla, spojovací čísla SIPO, IČO
"""

import re
import random
from datetime import date, timedelta


# ══════════════════════════════════════════════════════════════════════════════
# Čísla účtů
# ══════════════════════════════════════════════════════════════════════════════

# Váhy dle ČNB pro mod-11 kontrolu (pozice 1–10 zleva)
_ACCOUNT_WEIGHTS = [6, 3, 7, 9, 10, 5, 8, 4, 2, 1]


def _random_digits(count):
    """Vrátí seznam náhodných číslic dané délky; první číslice je vždy nenulová."""
    return [random.randint(1, 9)] + [random.randint(0, 9) for _ in range(count - 1)]


def _account_check_digit(digits):
    """
    Dopočítá poslední číslici (váha 1) tak, aby byl vážený součet dělitelný 11.
    Vstupem jsou číslice BEZ poslední pozice, zarovnají se doprava na 9 míst.
    Vrací 0–10; hodnota 10 znamená, že platná poslední číslice neexistuje.
    """
    padded = [0] * (9 - len(digits)) + digits
    return (-sum(d * w for d, w in zip(padded, _ACCOUNT_WEIGHTS[:9]))) % 11


def _generate_account_part(min_len, max_len):
    """
    Vygeneruje číslo (prefix nebo číslo účtu) validní dle mod-11.
    Číslo nemá úvodní nuly a je nenulové.
    """
    for _ in range(500):
        length = random.randint(min_len, max_len)
        digits = _random_digits(length - 1)
        last = _account_check_digit(digits)
        if last <= 9:
            digits.append(last)
            return ''.join(str(d) for d in digits)
    return None


def generate_iban(account_number, prefix, bank_code):
    """Vygeneruje IBAN pro CZ bankovní účet (MOD-97)."""
    bank_padded = str(bank_code).zfill(4)
    prefix_padded = str(prefix).zfill(6)
    account_padded = str(account_number).zfill(10)
    basic = bank_padded + prefix_padded + account_padded
    rearranged = basic + 'CZ00'
    numeric_str = ''.join(str(ord(ch) - ord('A') + 10) if ch.isalpha() else ch for ch in rearranged)
    check = 98 - (int(numeric_str) % 97)
    return f'CZ{check:02d}{basic}'


def format_iban(iban, grouped=False):
    """Formátuje IBAN; grouped=True oddělí každé 4 znaky mezerou."""
    if grouped:
        return ' '.join(iban[i:i+4] for i in range(0, len(iban), 4))
    return iban


def generate_account_numbers(count, with_prefix, without_prefix, bank_code=None, iban_format='plain'):
    """
    Vygeneruje čísla účtů.

    Vrátí (result, error) kde result = {'with_prefix': [...], 'without_prefix': [...]}.
    Pokud je bank_code zadán, položky jsou dicty {'account': ..., 'iban': ...},
    jinak prosté stringy (zpětná kompatibilita).
    """
    if not with_prefix and not without_prefix:
        return None, 'Zvol alespoň jednu variantu.'
    if not (1 <= count <= 100):
        return None, 'Počet musí být v rozmezí 1–100.'

    if bank_code and not re.fullmatch(r'\d{4}', str(bank_code)):
        return None, 'Kód banky musí mít přesně 4 číslice (0–9).'

    use_iban = bool(bank_code)
    result = {'with_prefix': [], 'without_prefix': []}

    for _ in range(count):
        if without_prefix:
            acc = _generate_account_part(6, 10)
            if not acc:
                return None, 'Generování čísla účtu selhalo, zkus to znovu.'
            if use_iban:
                iban = format_iban(generate_iban(acc, 0, bank_code), grouped=(iban_format == 'grouped'))
                result['without_prefix'].append({'account': acc, 'iban': iban})
            else:
                result['without_prefix'].append(acc)

        if with_prefix:
            acc = _generate_account_part(6, 10)
            prefix = _generate_account_part(2, 6)
            if not acc or not prefix:
                return None, 'Generování čísla účtu selhalo, zkus to znovu.'
            if use_iban:
                iban = format_iban(generate_iban(acc, prefix, bank_code), grouped=(iban_format == 'grouped'))
                result['with_prefix'].append({'account': f'{prefix}-{acc}', 'iban': iban})
            else:
                result['with_prefix'].append(f'{prefix}-{acc}')

    return result, None


def check_account_number(number):
    """
    Zkontroluje číslo dle mod-11 (ČNB) a případně navrhne opravu poslední číslice.

    Vrátí (result, error) kde result = {'valid': bool, 'number': ..., 'suggested': ...}.
    'suggested' je None, pokud je číslo platné nebo pokud oprava neexistuje
    (dopočet poslední číslice vyjde 10).
    """
    number = str(number).strip()
    if not re.fullmatch(r'\d{1,10}', number):
        return None, 'Číslo musí obsahovat 1–10 číslic (0–9).'

    digits = [int(ch) for ch in number]
    padded = [0] * (10 - len(digits)) + digits
    if sum(d * w for d, w in zip(padded, _ACCOUNT_WEIGHTS)) % 11 == 0:
        return {'valid': True, 'number': number, 'suggested': None}, None

    check = _account_check_digit(digits[:-1])
    suggested = number[:-1] + str(check) if check <= 9 else None
    return {'valid': False, 'number': number, 'suggested': suggested}, None


def check_account(number, bank_code=None):
    """
    Zkontroluje číslo účtu, volitelně ve formátu 'predcisli-cislo', a spočítá IBAN.

    Předčíslí (max 6 číslic) a číslo účtu (max 10 číslic) se kontrolují zvlášť
    stejnou mod-11 logikou. IBAN se počítá jen při zadaném kódu banky, a to
    z platného čísla (nebo z navržené opravy, pokud existuje).

    Vrátí (result, error) kde result = {'prefix': ..., 'account': ..., 'iban': ...}.
    """
    number = (number or '').strip()
    if not number:
        return None, 'Zadej číslo účtu.'
    if bank_code and not re.fullmatch(r'\d{4}', str(bank_code)):
        return None, 'Kód banky musí mít přesně 4 číslice (0–9).'

    if '-' in number:
        prefix_str, account_str = number.split('-', 1)
    else:
        prefix_str, account_str = None, number

    prefix_result = None
    if prefix_str is not None:
        if not re.fullmatch(r'\d{1,6}', prefix_str):
            return None, 'Předčíslí musí obsahovat 1–6 číslic (0–9).'
        prefix_result, error = check_account_number(prefix_str)
        if error:
            return None, error

    account_result, error = check_account_number(account_str)
    if error:
        return None, error

    # Pro IBAN použijeme platné číslo, jinak navrženou opravu (pokud existuje)
    final_account = account_result['number'] if account_result['valid'] else account_result['suggested']
    final_prefix = None
    if prefix_result:
        final_prefix = prefix_result['number'] if prefix_result['valid'] else prefix_result['suggested']

    iban = None
    if bank_code and final_account and (prefix_result is None or final_prefix):
        iban = generate_iban(final_account, final_prefix or 0, bank_code)

    return {'prefix': prefix_result, 'account': account_result, 'iban': iban}, None


# ══════════════════════════════════════════════════════════════════════════════
# Rodná čísla
# ══════════════════════════════════════════════════════════════════════════════

_CUTOFF_1954 = date(1954, 1, 1)

VARIANT_LABELS = {
    'old':          'Starý standard (XXX)',
    'new_normal':   'Nový standard (XXXX)',
    'new_extended': 'Nový standard +20/+70 (XXXX)',
}


def _subtract_years(d, years):
    """Odečte zadaný počet let od data; 29. 2. → 28. 2."""
    try:
        return d.replace(year=d.year - years)
    except ValueError:
        return d.replace(year=d.year - years, day=28)


def _random_date_in_age_range(age_min, age_max, upper_cutoff=None):
    """
    Vrátí náhodné datum narození pro osobu ve věku age_min–age_max let (k dnešnímu dni).
    Volitelný upper_cutoff omezuje horní hranici data (pro starý standard).
    """
    today = date.today()
    latest = _subtract_years(today, age_min)
    earliest = _subtract_years(today, age_max + 1) + timedelta(days=1)
    if upper_cutoff:
        latest = min(latest, upper_cutoff)
    if earliest > latest:
        return None
    return earliest + timedelta(days=random.randint(0, (latest - earliest).days))


def _encode_month(month, gender, variant):
    """Zakóduje měsíc pro rodné číslo dle pohlaví a varianty."""
    base = month if gender == 'M' else month + 50
    if variant == 'new_extended':
        base += 20
    return base


def _rc_old(birth_date, gender):
    """Starý standard: YYMMDD/SSS (bez mod-11 kontroly)."""
    yy = birth_date.year % 100
    mm = _encode_month(birth_date.month, gender, 'old')
    dd = birth_date.day
    sss = random.randint(1, 999)
    return f'{yy:02d}{mm:02d}{dd:02d}/{sss:03d}'


def _rc_new(birth_date, gender, variant, used_sss=None):
    """
    Nový standard: YYMMDD/SSSC — celé desetimístné číslo dělitelné 11.
    Volitelný used_sss (set) zajistí jedinečnost v rámci jednoho data+pohlaví+varianty.
    """
    yy = birth_date.year % 100
    mm = _encode_month(birth_date.month, gender, variant)
    dd = birth_date.day
    base6 = yy * 10000 + mm * 100 + dd

    candidates = list(range(1, 1000))
    random.shuffle(candidates)

    for sss in candidates:
        if used_sss is not None and sss in used_sss:
            continue
        num_without_c = base6 * 10000 + sss * 10
        c = (-num_without_c) % 11
        if c <= 9:
            if used_sss is not None:
                used_sss.add(sss)
            return f'{yy:02d}{mm:02d}{dd:02d}/{sss:03d}{c}'
    return None


def generate_birth_numbers(count, gender, variants, date_mode,
                           age_min=None, age_max=None, specific_date=None):
    """
    Vygeneruje rodná čísla.

    Parametry:
        count        – počet čísel (celkově, pro každou variantu)
        gender       – 'M', 'F', nebo 'both'
        variants     – list z ['old', 'new_normal', 'new_extended']
        date_mode    – 'range' nebo 'specific'
        age_min/max  – věkový rozsah (pro date_mode='range')
        specific_date – date objekt (pro date_mode='specific')

    Vrátí (results, error) kde results = {'old': [...], 'new_normal': [...], 'new_extended': [...]}.
    """
    if not variants:
        return None, 'Zvol alespoň jednu variantu.'
    if not (1 <= count <= 200):
        return None, 'Počet musí být v rozmezí 1–200.'

    # Validace starého standardu
    if 'old' in variants:
        if date_mode == 'specific':
            if specific_date >= _CUTOFF_1954:
                return None, (
                    'Starý standard je pouze pro osoby narozené před 1. 1. 1954. '
                    'Zadané datum je po tomto datu.'
                )
        else:
            # Zkontrolujeme, zda věkový rozsah vůbec může zasáhnout pre-1954 oblast
            today = date.today()
            earliest = _subtract_years(today, age_max + 1) + timedelta(days=1)
            if earliest >= _CUTOFF_1954:
                return None, (
                    f'Věkový rozsah {age_min}–{age_max} let nevede k datům před rokem 1954. '
                    'Starý standard vyžaduje věk alespoň 73 let (narození před 1. 1. 1954).'
                )

    # Sestavení seznamu pohlaví
    if gender == 'both':
        half = count // 2
        genders = ['M'] * half + ['F'] * (count - half)
        random.shuffle(genders)
    else:
        genders = [gender] * count

    results = {v: [] for v in variants}

    # Pro specific_date sledujeme použité SSS hodnoty per (variant, gender) pro jedinečnost
    used_sss_map = {}  # key: (variant, gender) → set

    for g in genders:
        for variant in variants:
            if date_mode == 'specific':
                birth_date = specific_date
            elif variant == 'old':
                # Pro starý standard omezíme datum na pre-1954 oblast
                birth_date = _random_date_in_age_range(
                    age_min, age_max,
                    upper_cutoff=date(1953, 12, 31)
                )
            else:
                birth_date = _random_date_in_age_range(age_min, age_max)

            if birth_date is None:
                return None, (
                    f'Nepodařilo se vygenerovat datum pro věkový rozsah {age_min}–{age_max} let.'
                )

            if variant == 'old':
                rc = _rc_old(birth_date, g)
            else:
                key = (variant, g, birth_date if date_mode == 'specific' else None)
                if date_mode == 'specific':
                    if key not in used_sss_map:
                        used_sss_map[key] = set()
                    rc = _rc_new(birth_date, g, variant, used_sss_map[key])
                else:
                    rc = _rc_new(birth_date, g, variant)

            if rc:
                results[variant].append(rc)
            # rc může být None jen při vyčerpání unikátních hodnot (extrémně vzácné)

    return results, None


# ══════════════════════════════════════════════════════════════════════════════
# SIPO
# ══════════════════════════════════════════════════════════════════════════════

# Váhy dle České pošty (Technické podmínky pro vstup Bank do SIPO, příloha č. 7)
_SIPO_WEIGHTS = [3, 7, 3, 1, 7, 3, 1, 7, 3]


def _sipo_check_digit(digits):
    """Dopočítá kontrolní číslici spojovacího čísla SIPO z prvních 9 číslic."""
    last = sum(d * w for d, w in zip(digits, _SIPO_WEIGHTS)) % 10
    return 0 if last == 0 else 10 - last


def generate_sipo(count):
    """
    Vygeneruje spojovací čísla SIPO (10 číslic: 9 náhodných + kontrolní číslice).

    Vrátí (result, error) kde result je seznam stringů.
    """
    if not (1 <= count <= 100):
        return None, 'Počet musí být v rozmezí 1–100.'

    numbers = []
    for _ in range(count):
        digits = _random_digits(9)
        numbers.append(''.join(str(d) for d in digits) + str(_sipo_check_digit(digits)))
    return numbers, None


# ══════════════════════════════════════════════════════════════════════════════
# IČO
# ══════════════════════════════════════════════════════════════════════════════

_ICO_WEIGHTS = [8, 7, 6, 5, 4, 3, 2]


def _ico_check_digit(digits):
    """Dopočítá kontrolní číslici IČO (mod-11) z prvních 7 číslic."""
    check = (11 - sum(d * w for d, w in zip(digits, _ICO_WEIGHTS))) % 11
    return (check or 1) % 10


def generate_ico(count):
    """
    Vygeneruje IČO (8 číslic: 7 náhodných + kontrolní číslice dle mod-11).

    Vrátí (result, error) kde result je seznam stringů.
    """
    if not (1 <= count <= 100):
        return None, 'Počet musí být v rozmezí 1–100.'

    numbers = []
    for _ in range(count):
        digits = _random_digits(7)
        numbers.append(''.join(str(d) for d in digits) + str(_ico_check_digit(digits)))
    return numbers, None
