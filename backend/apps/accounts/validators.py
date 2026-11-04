import re
from typing import Optional
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

# Limited whitelist of safe special characters for jewellery ERP POS systems
ALLOWED_SPECIAL_CHARS = set("@#$%*!&_")
ALLOWED_SPECIAL_CHARS_DISPLAY = "@ # $ % * ! & _"


def validate_password_policy(password: str) -> None:
    """
    Validates a password against the Swarna Khata Jewellery Shield Password Policy:
    1. Minimum length 8 characters, maximum 64 characters.
    2. At least one uppercase letter (A-Z).
    3. At least one lowercase letter (a-z).
    4. At least one numeric digit (0-9).
    5. At least one special character from the limited whitelist: @ # $ % * ! & _
    6. No disallowed characters outside [A-Za-z0-9@#$%*!&_].
    7. No consecutive duplicate characters (e.g. 'aa', '11', '@@').
    8. No consecutive sequential runs of 3+ letters or numbers (e.g. 'abc', '123', 'cba', '321').

    Raises:
        ValidationError: if any rule is violated.
    """
    if not password or len(password) < 8:
        raise ValidationError(
            _("Password must be at least 8 characters long."),
            code='password_too_short'
        )

    if len(password) > 64:
        raise ValidationError(
            _("Password cannot exceed 64 characters."),
            code='password_too_long'
        )

    if not re.search(r'[A-Z]', password):
        raise ValidationError(
            _("Password must contain at least one uppercase letter (A-Z)."),
            code='password_no_upper'
        )

    if not re.search(r'[a-z]', password):
        raise ValidationError(
            _("Password must contain at least one lowercase letter (a-z)."),
            code='password_no_lower'
        )

    if not re.search(r'\d', password):
        raise ValidationError(
            _("Password must contain at least one number (0-9)."),
            code='password_no_digit'
        )

    # Disallowed characters check (strict whitelist)
    disallowed = [c for c in password if not (c.isalnum() or c in ALLOWED_SPECIAL_CHARS)]
    if disallowed:
        unique_disallowed = "".join(sorted(set(disallowed)))
        raise ValidationError(
            _(f"Password contains disallowed character(s): '{unique_disallowed}'. Only {ALLOWED_SPECIAL_CHARS_DISPLAY} are allowed."),
            code='password_invalid_characters'
        )

    # At least one whitelisted special character
    if not any(c in ALLOWED_SPECIAL_CHARS for c in password):
        raise ValidationError(
            _(f"Password must contain at least one special character from: {ALLOWED_SPECIAL_CHARS_DISPLAY}"),
            code='password_no_special'
        )

    # Rule: Avoid consecutive duplicate characters (case-insensitive for letters, exact for others)
    lower_pass = password.lower()
    for i in range(len(lower_pass) - 1):
        if lower_pass[i] == lower_pass[i + 1]:
            sample = f"{password[i]}{password[i+1]}"
            raise ValidationError(
                _(f"Password must not contain consecutive identical characters (found '{sample}')."),
                code='password_consecutive_duplicates'
            )

    # Rule: Avoid consecutive sequential letters or numbers of length 3+
    # e.g., 'abc', 'xyz', 'cba', '123', '789', '321'
    for i in range(len(lower_pass) - 2):
        c1, c2, c3 = lower_pass[i], lower_pass[i + 1], lower_pass[i + 2]
        
        # Digits sequence (ascending or descending)
        if c1.isdigit() and c2.isdigit() and c3.isdigit():
            d1, d2, d3 = int(c1), int(c2), int(c3)
            if (d2 == d1 + 1 and d3 == d2 + 1) or (d2 == d1 - 1 and d3 == d2 - 1):
                sample = f"{password[i]}{password[i+1]}{password[i+2]}"
                raise ValidationError(
                    _(f"Password must not contain consecutive sequential numbers (found '{sample}')."),
                    code='password_sequential_numbers'
                )

        # Letters sequence (ascending or descending, case-insensitive)
        if c1.isalpha() and c2.isalpha() and c3.isalpha():
            o1, o2, o3 = ord(c1), ord(c2), ord(c3)
            if (o2 == o1 + 1 and o3 == o2 + 1) or (o2 == o1 - 1 and o3 == o2 - 1):
                sample = f"{password[i]}{password[i+1]}{password[i+2]}"
                raise ValidationError(
                    _(f"Password must not contain consecutive sequential letters (found '{sample}')."),
                    code='password_sequential_letters'
                )


class JewelleryPasswordPolicyValidator:
    """
    Django standard password validator complying with AUTH_PASSWORD_VALIDATORS.
    """
    def __init__(self, min_length: int = 8):
        self.min_length = min_length

    def validate(self, password: str, user: Optional[object] = None) -> None:
        validate_password_policy(password)

    def get_help_text(self) -> str:
        return _(
            "Your password must be at least 8 characters long, contain at least 1 uppercase letter, "
            "1 lowercase letter, 1 number, and 1 special character from [@, #, $, %, *, !, &, _]. "
            "Consecutive duplicate characters (like 'aa', '11') and sequential characters (like 'abc', '123') "
            "are not allowed."
        )


RESERVED_PLATFORM_USERNAMES = {
    'developer', 'superadmin', 'admin', 'root', 'system', 'swarna', 'support', 'public'
}


def check_global_username_uniqueness(
    username: str,
    exclude_user_id: Optional[int] = None,
    exclude_schema: Optional[str] = None
) -> None:
    """
    Validates that a username is unique across all tenant schemas and the public platform schema.
    1. Rejects usernames shorter than 3 characters or with invalid characters.
    2. Rejects platform-reserved usernames (developer, admin, root, etc.).
    3. Verifies no user exists in the public schema with the same username (case-insensitive).
    4. Iterates through all active tenant schemas to guarantee no collision anywhere.

    Raises:
        ValidationError: if the username is taken or reserved.
    """
    from django.conf import settings
    from django_tenants.utils import schema_context
    from apps.accounts.models import User
    from apps.tenants.models import Client

    clean_username = (username or '').strip()
    if not clean_username or len(clean_username) < 3:
        raise ValidationError(
            _("Username must be at least 3 characters long."),
            code='username_too_short'
        )

    if not re.match(r'^[a-zA-Z0-9_.-]+$', clean_username):
        raise ValidationError(
            _("Username can only contain letters, numbers, underscores, dots, and hyphens."),
            code='username_invalid_chars'
        )

    # Check against reserved platform usernames
    lower_user = clean_username.lower()
    dev_username = getattr(settings, 'DEVELOPER_SUPERUSER_USERNAME', 'developer').lower()
    if lower_user == dev_username or lower_user in RESERVED_PLATFORM_USERNAMES:
        if not (exclude_schema == 'public' and exclude_user_id):
            raise ValidationError(
                _(f"Username '{clean_username}' is reserved by the platform. Please choose a different username."),
                code='username_reserved'
            )

    # 1. Check public schema
    with schema_context('public'):
        qs = User.objects.filter(username__iexact=clean_username)
        if exclude_schema == 'public' and exclude_user_id:
            qs = qs.exclude(id=exclude_user_id)
        if qs.exists():
            raise ValidationError(
                _(f"Username '{clean_username}' is already in use."),
                code='username_taken'
            )

    # 2. Check all tenant schemas
    tenants = Client.objects.exclude(schema_name='public')
    for tenant in tenants:
        try:
            with schema_context(tenant.schema_name):
                qs = User.objects.filter(username__iexact=clean_username)
                if exclude_schema == tenant.schema_name and exclude_user_id:
                    qs = qs.exclude(id=exclude_user_id)
                if qs.exists():
                    raise ValidationError(
                        _(f"Username '{clean_username}' is already in use by store '{tenant.name}'."),
                        code='username_taken'
                    )
        except ValidationError:
            raise
        except Exception:
            # If a schema is mid-provisioning or table uninitialized, skip safely
            continue


def is_username_globally_available(username: str) -> bool:
    """Helper returning boolean availability without raising ValidationError."""
    try:
        check_global_username_uniqueness(username)
        return True
    except ValidationError:
        return False

