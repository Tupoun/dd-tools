"""
Autentizace — single-user, credentials z env proměnných.
"""
import os
from flask_login import UserMixin
from werkzeug.security import check_password_hash


class User(UserMixin):
    """Jednoduchý user objekt pro Flask-Login — vždy jen jeden uživatel."""
    id = "admin"

    @property
    def username(self):
        return os.getenv("ADMIN_USERNAME", "admin")


# Singleton instance
_user = User()


def get_user(user_id):
    """Vrátí uživatele pokud id odpovídá — volá Flask-Login při načtení session."""
    if user_id == _user.id:
        return _user
    return None


def verify_credentials(username, password):
    """Ověří username a heslo proti env proměnným. Vrátí User nebo None."""
    expected_username = os.getenv("ADMIN_USERNAME", "")
    expected_hash = os.getenv("ADMIN_PASSWORD_HASH", "")

    if not expected_username or not expected_hash:
        return None
    if username != expected_username:
        return None
    if not check_password_hash(expected_hash, password):
        return None
    return _user
