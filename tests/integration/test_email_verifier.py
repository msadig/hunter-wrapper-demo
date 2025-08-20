"""Integration tests for HunterClient.email_verifier method."""

import pytest
import requests

from hunter_wrapper.client import HunterClient


@pytest.mark.integration
class TestEmailVerifierIntegration:
    """Integration tests for email verification functionality."""

    def test_verify_valid_email(self, hunter_client: HunterClient, test_email: str) -> None:
        """Test verifying a valid email address.

        This test verifies that:
        1. The API accepts our request
        2. Returns expected data structure
        3. Provides verification status

        Args:
            hunter_client: Configured Hunter client instance.
            test_email: Test email address to verify.

        """
        verification_response = hunter_client.email_verifier(email=test_email)
        self._verify_response_structure(verification_response, test_email)

    def test_verify_invalid_email(self, hunter_client: HunterClient) -> None:
        """Test verifying an obviously invalid email address.

        Args:
            hunter_client: Configured Hunter client instance.

        """
        invalid_email = 'notanemail@nonexistentdomain123456.com'
        invalid_response = hunter_client.email_verifier(email=invalid_email)

        assert isinstance(invalid_response, dict), 'Response should be a dictionary'
        assert invalid_response['email'] == invalid_email, 'Response email should match requested email'

        # Invalid emails should have low scores
        low_score_threshold = 50
        assert invalid_response['score'] <= low_score_threshold, 'Invalid email should have low score'

    def test_verify_with_raw_response(self, hunter_client: HunterClient, test_email: str) -> None:
        """Test email verification with raw response flag.

        Args:
            hunter_client: Configured Hunter client instance.
            test_email: Test email address to verify.

        """
        raw_response = hunter_client.email_verifier(email=test_email, raw=True)

        # When raw=True, should return Response object
        assert isinstance(raw_response, requests.Response), 'Raw response should be requests.Response'
        expected_status = 200
        assert raw_response.status_code == expected_status, 'Should get successful response'

        # Parse JSON to verify structure
        json_data = raw_response.json()
        assert 'data' in json_data, 'Response should have data field'
        assert 'meta' in json_data, 'Response should have meta field'

    def test_verify_disposable_email(self, hunter_client: HunterClient) -> None:
        """Test verifying a disposable email address.

        Args:
            hunter_client: Configured Hunter client instance.

        """
        # Common disposable email domain
        disposable_email = 'test@mailinator.com'
        disposable_response = hunter_client.email_verifier(email=disposable_email)

        assert isinstance(disposable_response, dict), 'Response should be a dictionary'

        # Check if API correctly identifies disposable emails
        disposable_value = disposable_response.get('disposable')
        if disposable_value is not None:
            assert disposable_value is True, 'Should identify mailinator as disposable'

    def test_verify_webmail_email(self, hunter_client: HunterClient) -> None:
        """Test verifying a webmail address.

        Args:
            hunter_client: Configured Hunter client instance.

        """
        webmail_email = 'example@gmail.com'
        webmail_response = hunter_client.email_verifier(email=webmail_email)

        assert isinstance(webmail_response, dict), 'Response should be a dictionary'

        # Check if API correctly identifies webmail
        webmail_value = webmail_response.get('webmail')
        if webmail_value is not None:
            assert webmail_value is True, 'Should identify gmail as webmail'

    def test_api_response_consistency(self, hunter_client: HunterClient, test_email: str) -> None:
        """Test that multiple calls return consistent structure.

        Args:
            hunter_client: Configured Hunter client instance.
            test_email: Test email address to verify.

        """
        first_response = hunter_client.email_verifier(email=test_email)
        second_response = hunter_client.email_verifier(email=test_email)

        # Structure should be consistent
        assert set(first_response.keys()) == set(second_response.keys()), 'Response structure should be consistent'

        # Email field should match
        assert first_response['email'] == second_response['email'], 'Email should be consistent'
        assert first_response['email'] == test_email, 'Email should match test email'

    def _verify_response_structure(self, response: dict, test_email: str) -> None:
        """Verify email verification response structure.

        Args:
            response: Response dictionary from API.
            test_email: Expected email in response.

        """
        # Verify the response structure
        assert isinstance(response, dict), 'Response should be a dictionary'

        # Check for essential fields in the response
        expected_fields = {
            'status',
            'result',
            'score',
            'email',
            'regexp',
            'gibberish',
            'disposable',
            'webmail',
            'mx_records',
            'smtp_server',
            'smtp_check',
            'accept_all',
            'block',
            'sources',
        }

        missing_fields = expected_fields - set(response.keys())
        assert not missing_fields, 'Missing expected fields: {0}'.format(missing_fields)

        # Verify email in response matches request
        assert response['email'] == test_email, 'Response email should match requested email'

        # Verify score is in valid range
        assert 0 <= response['score'] <= 100, 'Score should be between 0 and 100'

        # Verify status is one of expected values
        assert response['status'] in {'valid', 'invalid', 'accept_all', 'unknown'}, 'Status should be valid'
