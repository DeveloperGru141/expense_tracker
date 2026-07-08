from app.core.security import sign_value, verify_signed_value


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
