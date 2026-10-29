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
