from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from apps.accounts.validators import validate_password_policy, JewelleryPasswordPolicyValidator


class PasswordPolicyTestCase(SimpleTestCase):
    """
    Unit tests for Jewellery Shield Password Policy:
    - 1+ capital letter
    - 1+ lowercase letter
    - 1+ number
    - 1+ special character from limited list [@, #, $, %, *, !, &, _]
    - No disallowed special characters
    - Avoid consecutive identical characters (e.g., aa, 11)
    - Avoid consecutive sequential letters or numbers (e.g., abc, 123)
    """

    def test_valid_passwords(self):
        valid_samples = [
            "Gold*Vault8",
            "Swarna#Khat9",
            "Kalyan@Shop7",
            "Diamond!Pos6",
            "Silver%Rat4",
            "Khata&Bhav3",
            "Safe_Vault2",
            "Jewel$Mark5",
        ]
        for pwd in valid_samples:
            try:
                validate_password_policy(pwd)
            except ValidationError as e:
                self.fail(f"Password '{pwd}' should be valid but failed with: {e.messages}")

    def test_missing_uppercase(self):
        with self.assertRaises(ValidationError) as ctx:
            validate_password_policy("swarna#khat9")
        self.assertIn("uppercase letter", ctx.exception.messages[0])

    def test_missing_lowercase(self):
        with self.assertRaises(ValidationError) as ctx:
            validate_password_policy("SWARNA#KHAT9")
        self.assertIn("lowercase letter", ctx.exception.messages[0])

    def test_missing_number(self):
        with self.assertRaises(ValidationError) as ctx:
            validate_password_policy("Swarna#Khata")
        self.assertIn("number", ctx.exception.messages[0])

    def test_missing_special_character(self):
        with self.assertRaises(ValidationError) as ctx:
            validate_password_policy("Swarna9Khata")
        self.assertIn("special character", ctx.exception.messages[0])

    def test_disallowed_special_characters(self):
        # '~', '<', '>', '"', ';' should be rejected
        disallowed_samples = [
            "Swarna~Khat9",
            "Swarna<Khat9>",
            "Swarna\"Khat9",
            "Swarna;Khat9",
        ]
        for pwd in disallowed_samples:
            with self.assertRaises(ValidationError) as ctx:
                validate_password_policy(pwd)
            self.assertIn("disallowed character", ctx.exception.messages[0])

    def test_consecutive_duplicate_letters(self):
        # 'ss' in 'Pass', 'ee' in 'Keen', 'Aa' in 'Aa'
        with self.assertRaises(ValidationError) as ctx:
            validate_password_policy("Pass#Word1")
        self.assertIn("consecutive identical characters", ctx.exception.messages[0])

        with self.assertRaises(ValidationError) as ctx:
            validate_password_policy("Gold#Keen1")
        self.assertIn("consecutive identical characters", ctx.exception.messages[0])

    def test_consecutive_duplicate_numbers(self):
        with self.assertRaises(ValidationError) as ctx:
            validate_password_policy("Gold*Vault88")
        self.assertIn("consecutive identical characters", ctx.exception.messages[0])

    def test_consecutive_sequential_numbers(self):
        # Ascending '123', descending '321'
        with self.assertRaises(ValidationError) as ctx:
            validate_password_policy("Gold*Shop123")
        self.assertIn("consecutive sequential numbers", ctx.exception.messages[0])

        with self.assertRaises(ValidationError) as ctx:
            validate_password_policy("Gold*Shop321")
        self.assertIn("consecutive sequential numbers", ctx.exception.messages[0])

    def test_consecutive_sequential_letters(self):
        # Ascending 'abc', descending 'cba'
        with self.assertRaises(ValidationError) as ctx:
            validate_password_policy("Gold$Abc9")
        self.assertIn("consecutive sequential letters", ctx.exception.messages[0])

        with self.assertRaises(ValidationError) as ctx:
            validate_password_policy("Gold$Cba9")
        self.assertIn("consecutive sequential letters", ctx.exception.messages[0])

    def test_django_validator_class(self):
        validator = JewelleryPasswordPolicyValidator()
        validator.validate("Gold*Vault8")
        with self.assertRaises(ValidationError):
            validator.validate("weak")
        self.assertTrue(len(validator.get_help_text()) > 10)
