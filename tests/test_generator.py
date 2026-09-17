"""Testy generátoru: SIPO, IČO a kontrola čísla účtu."""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from libs import generator


# ══════════════════════════════════════════════════════════════════════════════
# Nezávislé přepočty kontrolních číslic (round-trip ověření)
# ══════════════════════════════════════════════════════════════════════════════

SIPO_WEIGHTS = [3, 7, 3, 1, 7, 3, 1, 7, 3]
ICO_WEIGHTS = [8, 7, 6, 5, 4, 3, 2]
ACCOUNT_WEIGHTS = [6, 3, 7, 9, 10, 5, 8, 4, 2, 1]


def sipo_check_digit(digits):
    last = sum(d * w for d, w in zip(digits, SIPO_WEIGHTS)) % 10
    return 0 if last == 0 else 10 - last


def ico_check_digit(digits):
    check = (11 - sum(d * w for d, w in zip(digits, ICO_WEIGHTS))) % 11
    return (check or 1) % 10


def account_weighted_sum(number):
    digits = [int(ch) for ch in number]
    padded = [0] * (10 - len(digits)) + digits
    return sum(d * w for d, w in zip(padded, ACCOUNT_WEIGHTS))


# ══════════════════════════════════════════════════════════════════════════════
# SIPO
# ══════════════════════════════════════════════════════════════════════════════

def test_generate_sipo_count_and_length():
    result, error = generator.generate_sipo(20)
    assert error is None
    assert len(result) == 20
    for number in result:
        assert len(number) == 10
        assert number.isdigit()
        assert number[0] != '0'


def test_generate_sipo_check_digit_roundtrip():
    result, error = generator.generate_sipo(50)
    assert error is None
    for number in result:
        digits = [int(ch) for ch in number]
        assert digits[-1] == sipo_check_digit(digits[:9])


@pytest.mark.parametrize('count', [0, 101])
def test_generate_sipo_count_limits(count):
    result, error = generator.generate_sipo(count)
    assert result is None
    assert error


# ══════════════════════════════════════════════════════════════════════════════
# IČO
# ══════════════════════════════════════════════════════════════════════════════

def test_generate_ico_count_and_length():
    result, error = generator.generate_ico(20)
    assert error is None
    assert len(result) == 20
    for number in result:
        assert len(number) == 8
        assert number.isdigit()
        assert number[0] != '0'


def test_generate_ico_check_digit_roundtrip():
    result, error = generator.generate_ico(50)
    assert error is None
    for number in result:
        digits = [int(ch) for ch in number]
        assert digits[-1] == ico_check_digit(digits[:7])


def test_generate_ico_known_example():
    """Reálné IČO 25123891 – kontrolní číslice 1."""
    assert ico_check_digit([2, 5, 1, 2, 3, 8, 9]) == 1


@pytest.mark.parametrize('count', [0, 101])
def test_generate_ico_count_limits(count):
    result, error = generator.generate_ico(count)
    assert result is None
    assert error


# ══════════════════════════════════════════════════════════════════════════════
# Kontrola čísla účtu
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize('number', ['400004', '444404444', '19', '123'])
def test_check_account_number_valid(number):
    result, error = generator.check_account_number(number)
    assert error is None
    assert result == {'valid': True, 'number': number, 'suggested': None}
    assert account_weighted_sum(number) % 11 == 0


def test_check_account_number_invalid_with_suggestion():
    """1234567890: vážený součet 255, 255 % 11 == 2 → oprava na 1234567899."""
    assert account_weighted_sum('1234567890') == 255
    result, error = generator.check_account_number('1234567890')
    assert error is None
    assert result['valid'] is False
    assert result['suggested'] == '1234567899'
    assert account_weighted_sum(result['suggested']) % 11 == 0


def test_check_account_number_invalid_without_suggestion():
    """0400000000: dopočet poslední číslice vyjde 10 → oprava neexistuje."""
    result, error = generator.check_account_number('0400000000')
    assert error is None
    assert result['valid'] is False
    assert result['suggested'] is None


@pytest.mark.parametrize('number', ['', 'abc', '12345678901', '12a4'])
def test_check_account_number_bad_input(number):
    result, error = generator.check_account_number(number)
    assert result is None
    assert error


@pytest.mark.parametrize('number', ['19-19', '400004-444404444', '123-123'])
def test_check_account_prefix_and_account_valid(number):
    prefix_str, account_str = number.split('-')
    result, error = generator.check_account(number)
    assert error is None
    assert result['prefix'] == {'valid': True, 'number': prefix_str, 'suggested': None}
    assert result['account'] == {'valid': True, 'number': account_str, 'suggested': None}
    assert result['iban'] is None


def test_check_account_without_prefix():
    result, error = generator.check_account('19')
    assert error is None
    assert result['prefix'] is None
    assert result['account']['valid'] is True


def test_check_account_iban_only_with_bank_code():
    without, error = generator.check_account('19-19')
    assert error is None
    assert without['iban'] is None

    with_code, error = generator.check_account('19-19', bank_code='0800')
    assert error is None
    assert with_code['iban'] == generator.generate_iban('19', '19', '0800')


def test_check_account_iban_from_suggested_number():
    """U neplatného čísla se IBAN počítá z navržené opravy."""
    result, error = generator.check_account('1234567890', bank_code='0800')
    assert error is None
    assert result['account']['suggested'] == '1234567899'
    assert result['iban'] == generator.generate_iban('1234567899', 0, '0800')


def test_check_account_no_iban_when_fix_impossible():
    result, error = generator.check_account('0400000000', bank_code='0800')
    assert error is None
    assert result['account']['suggested'] is None
    assert result['iban'] is None


def test_check_account_invalid_bank_code():
    result, error = generator.check_account('19-19', bank_code='08')
    assert result is None
    assert error


@pytest.mark.parametrize('number', ['1234567-19', '19-12345678901', ''])
def test_check_account_bad_input(number):
    result, error = generator.check_account(number)
    assert result is None
    assert error
