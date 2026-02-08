"""Unit tests for inference service."""
import pytest
from unittest.mock import AsyncMock, Mock, patch
import httpx

from src.services.inference import InferenceClient


class TestInferenceClient:
    """Test suite for InferenceClient."""

    @pytest.fixture
    def client(self):
        """Create an InferenceClient instance for testing."""
        return InferenceClient(base_url="http://test-tgi:8080", timeout=10.0, max_retries=2)

    @pytest.fixture
    def mock_httpx_client(self):
        """Create a mock httpx.AsyncClient."""
        mock = AsyncMock()
        return mock

    async def test_init_default_values(self):
        """Test client initialization with default values."""
        with patch("src.services.inference.settings") as mock_settings:
            mock_settings.inference_url = "http://default-url:8080"
            client = InferenceClient()

            assert client.base_url == "http://default-url:8080"
            assert client.timeout == 30.0
            assert client.max_retries == 3

    async def test_init_custom_values(self):
        """Test client initialization with custom values."""
        client = InferenceClient(
            base_url="http://custom:9090",
            timeout=60.0,
            max_retries=5
        )

        assert client.base_url == "http://custom:9090"
        assert client.timeout == 60.0
        assert client.max_retries == 5

    async def test_context_manager(self, client):
        """Test async context manager functionality."""
        async with client as ctx_client:
            assert ctx_client is client

        # Client should be closed after context exit
        # We can't directly test if client is closed, but we verify no errors

    async def test_complete_success(self, client, mock_httpx_client):
        """Test successful completion request."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"text": "Generated completion text"}]
        }
        mock_response.raise_for_status = Mock()
        mock_httpx_client.request.return_value = mock_response

        client.client = mock_httpx_client

        result = await client.complete("Test prompt")

        assert result == "Generated completion text"
        mock_httpx_client.request.assert_called_once()
        call_args = mock_httpx_client.request.call_args
        assert call_args[0][0] == "POST"
        assert call_args[0][1] == "http://test-tgi:8080/v1/completions"
        assert call_args[1]["json"]["prompt"] == "Test prompt"

    async def test_complete_custom_params(self, client, mock_httpx_client):
        """Test completion with custom parameters."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"text": "Custom completion"}]
        }
        mock_response.raise_for_status = Mock()
        mock_httpx_client.request.return_value = mock_response

        client.client = mock_httpx_client

        result = await client.complete(
            "Test prompt",
            max_tokens=1024,
            temperature=0.9,
            top_p=0.95
        )

        assert result == "Custom completion"
        call_args = mock_httpx_client.request.call_args
        payload = call_args[1]["json"]
        assert payload["max_tokens"] == 1024
        assert payload["temperature"] == 0.9
        assert payload["top_p"] == 0.95

    async def test_complete_empty_response(self, client, mock_httpx_client):
        """Test completion with empty choices."""
        mock_response = Mock()
        mock_response.json.return_value = {"choices": []}
        mock_response.raise_for_status = Mock()
        mock_httpx_client.request.return_value = mock_response

        client.client = mock_httpx_client

        result = await client.complete("Test prompt")

        assert result == ""

    async def test_complete_unexpected_format(self, client, mock_httpx_client):
        """Test completion with unexpected response format."""
        mock_response = Mock()
        mock_response.json.return_value = {"unexpected": "format"}
        mock_response.raise_for_status = Mock()
        mock_httpx_client.request.return_value = mock_response

        client.client = mock_httpx_client

        result = await client.complete("Test prompt")

        assert result == ""

    async def test_complete_http_error(self, client, mock_httpx_client):
        """Test completion handling HTTP errors."""
        mock_httpx_client.request.side_effect = httpx.HTTPStatusError(
            "500 Server Error",
            request=Mock(),
            response=Mock(status_code=500)
        )

        client.client = mock_httpx_client

        with pytest.raises(httpx.HTTPStatusError):
            await client.complete("Test prompt")

    async def test_chat_success(self, client, mock_httpx_client):
        """Test successful chat completion request."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Chat response"}}]
        }
        mock_response.raise_for_status = Mock()
        mock_httpx_client.request.return_value = mock_response

        client.client = mock_httpx_client

        messages = [
            {"role": "user", "content": "Hello"}
        ]
        result = await client.chat(messages)

        assert result == "Chat response"
        mock_httpx_client.request.assert_called_once()
        call_args = mock_httpx_client.request.call_args
        assert call_args[0][0] == "POST"
        assert call_args[0][1] == "http://test-tgi:8080/v1/chat/completions"
        assert call_args[1]["json"]["messages"] == messages

    async def test_chat_custom_params(self, client, mock_httpx_client):
        """Test chat with custom parameters."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Chat response"}}]
        }
        mock_response.raise_for_status = Mock()
        mock_httpx_client.request.return_value = mock_response

        client.client = mock_httpx_client

        messages = [{"role": "user", "content": "Hello"}]
        result = await client.chat(
            messages,
            max_tokens=2048,
            temperature=0.5
        )

        assert result == "Chat response"
        call_args = mock_httpx_client.request.call_args
        payload = call_args[1]["json"]
        assert payload["max_tokens"] == 2048
        assert payload["temperature"] == 0.5

    async def test_chat_empty_response(self, client, mock_httpx_client):
        """Test chat with empty choices."""
        mock_response = Mock()
        mock_response.json.return_value = {"choices": []}
        mock_response.raise_for_status = Mock()
        mock_httpx_client.request.return_value = mock_response

        client.client = mock_httpx_client

        result = await client.chat([{"role": "user", "content": "Hello"}])

        assert result == ""

    async def test_chat_http_error(self, client, mock_httpx_client):
        """Test chat handling HTTP errors."""
        mock_httpx_client.request.side_effect = httpx.HTTPStatusError(
            "503 Service Unavailable",
            request=Mock(),
            response=Mock(status_code=503)
        )

        client.client = mock_httpx_client

        with pytest.raises(httpx.HTTPStatusError):
            await client.chat([{"role": "user", "content": "Hello"}])

    async def test_health_check_success_health_endpoint(self, client, mock_httpx_client):
        """Test health check using /health endpoint."""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "ok"}
        mock_response.raise_for_status = Mock()
        mock_httpx_client.request.return_value = mock_response

        client.client = mock_httpx_client

        result = await client.health_check()

        assert result is True
        mock_httpx_client.request.assert_called_once()
        call_args = mock_httpx_client.request.call_args
        assert call_args[0][0] == "GET"
        assert call_args[0][1] == "http://test-tgi:8080/health"

    async def test_health_check_fallback_to_completion(self, client, mock_httpx_client):
        """Test health check falling back to completion when /health fails."""
        # First call to /health fails
        health_error = httpx.HTTPStatusError(
            "404 Not Found",
            request=Mock(),
            response=Mock(status_code=404)
        )
        # Second call to completion succeeds
        completion_response = Mock()
        completion_response.json.return_value = {
            "choices": [{"text": "test"}]
        }
        completion_response.raise_for_status = Mock()

        mock_httpx_client.request.side_effect = [health_error, completion_response]

        client.client = mock_httpx_client

        result = await client.health_check()

        assert result is True
        assert mock_httpx_client.request.call_count == 2

    async def test_health_check_unhealthy(self, client, mock_httpx_client):
        """Test health check when service is unhealthy."""
        mock_httpx_client.request.side_effect = httpx.HTTPStatusError(
            "500 Server Error",
            request=Mock(),
            response=Mock(status_code=500)
        )

        client.client = mock_httpx_client

        result = await client.health_check()

        assert result is False

    async def test_retry_logic_success_on_second_attempt(self, client, mock_httpx_client):
        """Test retry logic succeeds on second attempt."""
        # First call fails, second succeeds
        error = httpx.HTTPStatusError(
            "503 Service Unavailable",
            request=Mock(),
            response=Mock(status_code=503)
        )
        success_response = Mock()
        success_response.json.return_value = {
            "choices": [{"text": "Success after retry"}]
        }
        success_response.raise_for_status = Mock()

        mock_httpx_client.request.side_effect = [error, success_response]

        client.client = mock_httpx_client

        with patch("asyncio.sleep") as mock_sleep:  # Mock sleep to speed up test
            result = await client.complete("Test prompt")

        assert result == "Success after retry"
        assert mock_httpx_client.request.call_count == 2
        mock_sleep.assert_called_once_with(1)  # First backoff is 2^0 = 1 second

    async def test_retry_logic_exhausts_retries(self, client, mock_httpx_client):
        """Test retry logic exhausts all retries and raises error."""
        error = httpx.HTTPStatusError(
            "503 Service Unavailable",
            request=Mock(),
            response=Mock(status_code=503)
        )
        mock_httpx_client.request.side_effect = error

        client.client = mock_httpx_client

        with patch("asyncio.sleep") as mock_sleep:
            with pytest.raises(httpx.HTTPStatusError):
                await client.complete("Test prompt")

        assert mock_httpx_client.request.call_count == 2  # max_retries=2
        # Should sleep twice: 1s and 2s (2^0 and 2^1)
        assert mock_sleep.call_count == 1  # Only one retry, so one sleep

    async def test_retry_logic_exponential_backoff(self, client, mock_httpx_client):
        """Test exponential backoff timing."""
        client.max_retries = 3
        error = httpx.HTTPStatusError(
            "503 Service Unavailable",
            request=Mock(),
            response=Mock(status_code=503)
        )
        mock_httpx_client.request.side_effect = error

        client.client = mock_httpx_client

        with patch("asyncio.sleep") as mock_sleep:
            with pytest.raises(httpx.HTTPStatusError):
                await client.complete("Test prompt")

        # Should have 2 sleep calls: 1s and 2s (attempts 1 and 2, before attempt 3)
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(1)  # 2^0
        mock_sleep.assert_any_call(2)  # 2^1

    async def test_timeout_handling(self, client, mock_httpx_client):
        """Test timeout handling."""
        mock_httpx_client.request.side_effect = httpx.TimeoutException(
            "Request timed out"
        )

        client.client = mock_httpx_client

        with pytest.raises(httpx.TimeoutException):
            await client.complete("Test prompt")

    async def test_close(self, client, mock_httpx_client):
        """Test closing the client."""
        client.client = mock_httpx_client

        await client.close()

        mock_httpx_client.aclose.assert_called_once()
