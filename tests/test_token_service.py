import pytest
from webapp.services import TokenService


class TestTokenService:
    def test_generate_default_length(self):
        """Test token generation with default length."""
        service = TokenService()
        token = service.generate()
        assert len(token) == 20
        assert isinstance(token, str)

    def test_generate_custom_length(self):
        """Test token generation with custom length."""
        service = TokenService()
        token = service.generate(10)
        assert len(token) == 10

    def test_generate_different_tokens(self):
        """Test that generated tokens are different (pseudo-random)."""
        service = TokenService()
        token1 = service.generate()
        token2 = service.generate()
        assert token1 != token2

    def test_generate_base64_characters(self):
        """Test that tokens contain valid base64 characters."""
        service = TokenService()
        token = service.generate()
        import string
        valid_chars = string.ascii_letters + string.digits + '+/='
        assert all(c in valid_chars for c in token)

    def test_generate_zero_length(self):
        """Test token generation with length 0."""
        service = TokenService()
        token = service.generate(0)
        assert token == ''

    def test_generate_negative_length(self):
        """Test token generation rejects negative lengths."""
        service = TokenService()
        with pytest.raises(ValueError, match="non-negative"):
            service.generate(-1)

    def test_generate_large_length(self):
        """Test token generation with large length (max ~88 due to base64 of 64 bytes)."""
        service = TokenService()
        token = service.generate(80)
        assert len(token) == 80
