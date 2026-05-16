#!/usr/bin/env python3
"""
Jednorázový skript pro vygenerování ADMIN_PASSWORD_HASH.
Spusť: python generate_password.py
Výstup zkopíruj do .env jako ADMIN_PASSWORD_HASH=<hash>
"""
from werkzeug.security import generate_password_hash
import getpass

password = getpass.getpass("Zadej heslo: ")
confirm = getpass.getpass("Potvrď heslo: ")

if password != confirm:
    print("Hesla se neshodují.")
else:
    print(f"\nADMIN_PASSWORD_HASH={generate_password_hash(password)}")
