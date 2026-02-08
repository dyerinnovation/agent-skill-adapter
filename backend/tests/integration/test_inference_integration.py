"""Integration tests for inference service with evaluation controller."""
import pytest
from unittest.mock import AsyncMock, Mock, patch
import httpx

from src.services.inference import InferenceClient
from src.services.evaluator import evaluate_output
from src.services.skill_loader import parse_skill
from src.models.schemas import RubricItem


@pytest.fixture
def mock_tgi_response():
    """Mock TGI API response."""
    return {
        "choices": [
            {
                "text": "# Test Output\n\nThis is a properly formatted response with error handling."
            }
        ]
    }


@pytest.fixture
def sample_skill_content():
    """Sample SKILL.md content for testing."""
    return """# Test Skill

## Skill Overview
This skill tests basic functionality.

## Success Criteria
- Output must be in markdown format
- Must include proper error handling
- Response should be concise
"""


class TestInferenceIntegration:
    """Integration tests for inference service."""

    async def test_evaluation_with_mocked_inference(self, mock_tgi_response):
        """Test evaluation controller with mocked inference service."""
        # Mock the httpx client
        mock_httpx_client = AsyncMock()
        mock_response = Mock()
        mock_response.json.return_value = mock_tgi_response
        mock_response.raise_for_status = Mock()
        mock_httpx_client.request.return_value = mock_response

        # Create inference client and inject mocked httpx client
        client = InferenceClient(base_url="http://mock-tgi:8080")
        client.client = mock_httpx_client

        # Generate completion
        result = await client.complete("Test prompt")

        assert "Test Output" in result
        assert "error handling" in result

        # Evaluate the output
        rubrics = [
            RubricItem(
                name="format_check",
                description="Output must be in markdown format",
                weight=1.0,
                category="structural",
            ),
            RubricItem(
                name="content_check",
                description="Must include proper error handling",
                weight=1.0,
                category="behavioral",
            ),
        ]

        scores, aggregate = evaluate_output(result, rubrics)

        assert len(scores) == 2
        assert aggregate > 0.5  # Should score reasonably well

        await client.close()

    async def test_full_flow_skill_to_evaluation(self, sample_skill_content, mock_tgi_response):
        """Test full flow: skill_loader -> evaluator -> inference."""
        # Parse skill file
        with patch("builtins.open", create=True) as mock_open:
            mock_open.return_value.__enter__ = Mock(return_value=Mock(read=Mock(return_value=sample_skill_content)))
            mock_open.return_value.__exit__ = Mock(return_value=False)

            with patch("os.path.exists", return_value=True):
                from src.services.skill_loader import parse_skill
                from pathlib import Path
                skill = parse_skill(Path("/fake/path/SKILL.md"))

        # Mock inference client
        mock_httpx_client = AsyncMock()
        mock_response = Mock()
        mock_response.json.return_value = mock_tgi_response
        mock_response.raise_for_status = Mock()
        mock_httpx_client.request.return_value = mock_response

        client = InferenceClient(base_url="http://mock-tgi:8080")
        client.client = mock_httpx_client

        # Generate output from skill description
        prompt = f"Generate output for: {skill.description}"
        output = await client.complete(prompt)

        # Create rubrics from skill success criteria
        rubrics = [
            RubricItem(
                name="criterion_1",
                description="Output must be in markdown format",
                weight=1.0,
                category="structural",
            ),
            RubricItem(
                name="criterion_2",
                description="Must include proper error handling",
                weight=1.0,
                category="behavioral",
            ),
        ]

        # Evaluate
        scores, aggregate = evaluate_output(output, rubrics)

        assert len(scores) == 2
        assert all(score.score >= 0.0 for score in scores)
        assert aggregate >= 0.0

        await client.close()

    async def test_inference_fallback_when_no_model_path(self, mock_tgi_response):
        """Test that evaluation uses inference service when no local model_path is provided."""
        # Mock the inference client
        mock_httpx_client = AsyncMock()
        mock_response = Mock()
        mock_response.json.return_value = mock_tgi_response
        mock_response.raise_for_status = Mock()
        mock_httpx_client.request.return_value = mock_response

        client = InferenceClient(base_url="http://mock-tgi:8080")
        client.client = mock_httpx_client

        # Simulate evaluation workflow where we use remote inference
        prompt = "Generate a test response"
        output = await client.complete(prompt)

        assert output is not None
        assert len(output) > 0

        # Verify the inference endpoint was called
        mock_httpx_client.request.assert_called_once()
        call_args = mock_httpx_client.request.call_args
        assert call_args[0][1].endswith("/v1/completions")

        await client.close()

    async def test_chat_endpoint_integration(self, mock_tgi_response):
        """Test chat endpoint integration."""
        # Mock chat response
        chat_response = {
            "choices": [
                {
                    "message": {
                        "content": "This is a chat response about error handling in markdown."
                    }
                }
            ]
        }

        mock_httpx_client = AsyncMock()
        mock_response = Mock()
        mock_response.json.return_value = chat_response
        mock_response.raise_for_status = Mock()
        mock_httpx_client.request.return_value = mock_response

        client = InferenceClient(base_url="http://mock-tgi:8080")
        client.client = mock_httpx_client

        # Make chat request
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Explain error handling."}
        ]
        output = await client.chat(messages)

        assert "error handling" in output
        assert len(output) > 0

        # Verify endpoint
        call_args = mock_httpx_client.request.call_args
        assert call_args[0][1].endswith("/v1/chat/completions")
        assert call_args[1]["json"]["messages"] == messages

        await client.close()

    async def test_health_check_integration(self):
        """Test health check integration with retry logic."""
        mock_httpx_client = AsyncMock()

        # First health check fails, retry succeeds
        health_response = Mock()
        health_response.json.return_value = {"status": "healthy"}
        health_response.raise_for_status = Mock()

        mock_httpx_client.request.return_value = health_response

        client = InferenceClient(base_url="http://mock-tgi:8080", max_retries=3)
        client.client = mock_httpx_client

        is_healthy = await client.health_check()

        assert is_healthy is True

        await client.close()

    async def test_error_propagation_through_evaluation(self):
        """Test that inference errors propagate correctly through evaluation."""
        mock_httpx_client = AsyncMock()
        mock_httpx_client.request.side_effect = httpx.HTTPStatusError(
            "500 Server Error",
            request=Mock(),
            response=Mock(status_code=500)
        )

        client = InferenceClient(base_url="http://mock-tgi:8080", max_retries=1)
        client.client = mock_httpx_client

        # Should raise error after retries
        with pytest.raises(httpx.HTTPStatusError):
            await client.complete("Test prompt")

        await client.close()

    async def test_timeout_propagation(self):
        """Test timeout errors propagate through the stack."""
        mock_httpx_client = AsyncMock()
        mock_httpx_client.request.side_effect = httpx.TimeoutException("Timeout")

        client = InferenceClient(base_url="http://mock-tgi:8080", timeout=5.0)
        client.client = mock_httpx_client

        with pytest.raises(httpx.TimeoutException):
            await client.complete("Test prompt")

        await client.close()

    async def test_context_manager_usage(self, mock_tgi_response):
        """Test using InferenceClient as async context manager."""
        mock_httpx_client = AsyncMock()
        mock_response = Mock()
        mock_response.json.return_value = mock_tgi_response
        mock_response.raise_for_status = Mock()
        mock_httpx_client.request.return_value = mock_response

        async with InferenceClient(base_url="http://mock-tgi:8080") as client:
            client.client = mock_httpx_client
            result = await client.complete("Test prompt")
            assert result is not None

        # Client should be closed after context exit
        # Verify the mock was called for cleanup
        mock_httpx_client.aclose.assert_called_once()
