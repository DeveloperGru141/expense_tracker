from app.core.security import get_password_hash, verify_password, sign_value, verify_signed_value


class TestPasswordHashing:
    def test_hash_and_verify(self):
        password = "MySecureP@ss123!"
        hashed = get_password_hash(password)
        assert hashed != password
        assert verify_password(password, hashed) is True

    def test_wrong_password_fails(self):
        hashed = get_password_hash("correct_password")
        assert verify_password("wrong_password", hashed) is False

    def test_long_password_truncation(self):
        long_pw = "a" * 200
        hashed = get_password_hash(long_pw)
        assert verify_password(long_pw, hashed) is True
        # bcrypt truncates at 72 bytes, so a different tail should also match
        assert verify_password("a" * 200 + "different", hashed) is True

    def test_empty_password(self):
        hashed = get_password_hash("")
        assert verify_password("", hashed) is True


class TestSignedValues:
    def test_sign_and_verify(self):
        signed = sign_value("user_session_123")
        assert signed.startswith("user_session_123.")
        assert verify_signed_value(signed) == "user_session_123"

    def test_none_returns_none(self):
        assert verify_signed_value(None) is None

    def test_empty_string(self):
        assert verify_signed_value("") is None

    def test_tampered_signature_fails(self):
        signed = sign_value("user_session_123")
        parts = signed.split(".")
        tampered = f"{parts[0]}.0000000000000000000000000000000000000000000000000000000000000000"
        assert verify_signed_value(tampered) is None

    def test_no_dot_returns_none(self):
        assert verify_signed_value("notamperedvalue") is None


class TestCsrfToken:
    def test_token_is_string(self):
        from app.core.security import get_csrf_token
        from unittest.mock import MagicMock
        request = MagicMock()
        request.cookies = {}
        token = get_csrf_token(request)
        assert isinstance(token, str)
        assert len(token) > 0
