"""Pytest configuration for Hunter wrapper tests."""

import os

import pytest
from dotenv import load_dotenv

from hunter_wrapper.client import HunterClient

# Load environment variables from .env file
load_dotenv()


@pytest.fixture(scope='session')
def hunter_api_key() -> str:
    """Get Hunter API key from environment.

    Returns:
        The Hunter API key.

    Raises:
        ValueError: If HUNTER_API_KEY is not set in environment.

    """
    api_key_from_env = os.getenv('HUNTER_API_KEY')
    if not api_key_from_env:
        error_parts = [
            'HUNTER_API_KEY environment variable is required for integration tests.',
            'Please set it in your .env file or environment variables.',
        ]
        error_message = ' '.join(error_parts)
        raise ValueError(error_message)
    return api_key_from_env


@pytest.fixture(scope='session', name='hunter_client')
def create_hunter_client(hunter_api_key: str) -> HunterClient:  # noqa: WPS442
    """Create a HunterClient instance for testing.

    Args:
        hunter_api_key: The Hunter API key from fixture.

    Returns:
        A configured HunterClient instance.

    """
    return HunterClient(api_key=hunter_api_key)


@pytest.fixture
def test_email() -> str:
    """Provide a test email address.

    Returns:
        A test email address that should exist.

    """
    return 'patrick@stripe.com'


@pytest.fixture
def test_domain() -> str:
    """Provide a test domain.

    Returns:
        A test domain for domain search tests.

    """
    return 'stripe.com'


@pytest.fixture
def test_company() -> str:
    """Provide a test company name.

    Returns:
        A test company name for search tests.

    """
    return 'Hunter'


@pytest.fixture
def test_person_data() -> dict:
    """Provide test person data for email finder.

    Returns:
        Dictionary with person data for testing.

    """
    return {
        'first_name': 'Kevin',
        'last_name': 'Systrom',
        'domain': 'instagram.com',
    }


def pytest_configure(config):
    """Configure pytest with custom markers.

    Args:
        config: Pytest configuration object.

    """
    config.addinivalue_line(
        'markers',
        'integration: mark test as integration test (requires API key)',
    )
    config.addinivalue_line(
        'markers',
        'slow: mark test as slow running',
    )
