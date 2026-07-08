from app.api.utils import validate_redirect_url


class TestValidateRedirectUrl:
    def test_valid_relative(self):
        assert validate_redirect_url("/expenses") == "/expenses"
        assert validate_redirect_url("/dashboard") == "/dashboard"
        assert validate_redirect_url("/recurring") == "/recurring"

    def test_root_path(self):
        assert validate_redirect_url("/") == "/"

    def test_open_redirect_external(self):
        assert validate_redirect_url("https://evil.com") == "/dashboard"

    def test_open_redirect_protocol_relative(self):
        assert validate_redirect_url("//evil.com") == "/dashboard"

    def test_open_redirect_with_path(self):
        assert validate_redirect_url("https://evil.com/phish") == "/dashboard"

    def test_empty_string(self):
        assert validate_redirect_url("") == "/dashboard"

    def test_long_url(self):
        long_url = "/" + "a" * 500
        result = validate_redirect_url(long_url)
        assert result == long_url
