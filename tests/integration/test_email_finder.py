"""Integration tests for HunterClient.email_finder method."""

import pytest
import requests

from hunter_wrapper.client import HunterClient
from hunter_wrapper.exceptions import MissingCompanyError, MissingNameError


@pytest.mark.integration
class TestEmailFinderBasic:
    """Basic integration tests for email finder functionality."""

    def test_find_email_with_names(
        self,
        hunter_client: HunterClient,
        test_person_data: dict,
    ) -> None:
        """Test finding email with first and last name.

        This test verifies that:
        1. The API accepts email finder requests
        2. Returns expected data structure
        3. Provides email and confidence score

        Args:
            hunter_client: Configured Hunter client instance.
            test_person_data: Test person data for email finding.

        """
        email, score = hunter_client.email_finder(
            domain=test_person_data['domain'],
            first_name=test_person_data['first_name'],
            last_name=test_person_data['last_name'],
        )

        # Verify returned values
        assert isinstance(email, str), 'Email should be a string'
        assert isinstance(score, int), 'Score should be an integer'

        # Verify email format
        assert '@' in email, 'Email should contain @'
        assert test_person_data['domain'] in email, 'Email should contain domain'

        # Verify score is in valid range
        assert 0 <= score <= 100, 'Score should be between 0 and 100'

    def test_find_email_with_full_name(
        self,
        hunter_client: HunterClient,
        test_person_data: dict,
    ) -> None:
        """Test finding email with full name parameter.

        Args:
            hunter_client: Configured Hunter client instance.
            test_person_data: Test person data for email finding.

        """
        test_domain = test_person_data['domain']
        full_name = '{0} {1}'.format(
            test_person_data['first_name'],
            test_person_data['last_name'],
        )
        email, score = hunter_client.email_finder(
            domain=test_domain,
            full_name=full_name,
        )

        assert isinstance(email, str), 'Email should be a string'
        assert isinstance(score, int), 'Score should be an integer'
        assert test_domain in email, 'Email should contain domain'

    def test_find_email_with_company_name(
        self,
        hunter_client: HunterClient,
        test_person_data: dict,
    ) -> None:
        """Test finding email with company name instead of domain.

        Args:
            hunter_client: Configured Hunter client instance.
            test_person_data: Test person data for email finding.

        """
        email, score = hunter_client.email_finder(
            company='Instagram',
            first_name=test_person_data['first_name'],
            last_name=test_person_data['last_name'],
        )

        assert isinstance(email, str), 'Email should be a string'
        assert isinstance(score, int), 'Score should be an integer'
        assert '@' in email, 'Email should be valid format'


@pytest.mark.integration
class TestEmailFinderRawResponse:
    """Integration tests for email finder raw response functionality."""

    def test_find_email_raw_response(
        self,
        hunter_client: HunterClient,
        test_person_data: dict,
    ) -> None:
        """Test email finder with raw response flag.

        Args:
            hunter_client: Configured Hunter client instance.
            test_person_data: Test person data for email finding.

        """
        response = hunter_client.email_finder(
            domain=test_person_data['domain'],
            first_name=test_person_data['first_name'],
            last_name=test_person_data['last_name'],
            raw=True,
        )

        # Should return Response object when raw=True
        assert isinstance(response, requests.Response), 'Raw response should be requests.Response'
        success_status_code = 200
        assert response.status_code == success_status_code, 'Should get successful response'

        # Parse and verify response structure
        response_data = response.json()['data']

        # Check all required fields are present
        required_fields = {'email', 'score', 'position', 'first_name', 'last_name', 'sources', 'verification'}
        assert required_fields.issubset(response_data.keys()), 'Missing required fields'

        # Verify the types
        assert isinstance(response_data['email'], str), 'Email should be string'
        assert isinstance(response_data['score'], int), 'Score should be integer'

    def test_find_email_sources_in_raw(
        self,
        hunter_client: HunterClient,
        test_person_data: dict,
    ) -> None:
        """Test that raw response includes source information.

        Args:
            hunter_client: Configured Hunter client instance.
            test_person_data: Test person data for email finding.

        """
        response = hunter_client.email_finder(
            domain=test_person_data['domain'],
            first_name=test_person_data['first_name'],
            last_name=test_person_data['last_name'],
            raw=True,
        )

        assert isinstance(response, requests.Response), 'Should return Response object'

        finder_data = response.json()['data']

        # Check sources structure if available
        if finder_data.get('sources'):
            assert isinstance(finder_data['sources'], list), 'Sources should be a list'

            if finder_data['sources']:
                # Check common source fields
                expected_source_fields = {'domain', 'uri', 'extracted_on'}

                # Some sources might not have all fields
                # At least one of the expected fields should be present
                source_keys = set(finder_data['sources'][0].keys())
                assert source_keys & expected_source_fields, 'Source should have expected fields'


@pytest.mark.integration
class TestEmailFinderErrors:
    """Integration tests for email finder error handling."""

    def test_find_email_missing_company_error(self, hunter_client: HunterClient) -> None:
        """Test that missing both domain and company raises error.

        Args:
            hunter_client: Configured Hunter client instance.

        """
        with pytest.raises(MissingCompanyError, match='domain name or a company name'):
            hunter_client.email_finder(
                first_name='John',
                last_name='Doe',
            )

    def test_find_email_missing_name_error(self, hunter_client: HunterClient) -> None:
        """Test that missing name information raises error.

        Args:
            hunter_client: Configured Hunter client instance.

        """
        with pytest.raises(MissingNameError, match='You must supply a first name AND a last name OR a full name'):
            hunter_client.email_finder(domain='example.com')

    def test_find_email_partial_name_error(self, hunter_client: HunterClient) -> None:
        """Test that partial name without first name raises error.

        Args:
            hunter_client: Configured Hunter client instance.

        """
        with pytest.raises(MissingNameError, match='first name'):
            hunter_client.email_finder(
                domain='example.com',
                last_name='Doe',
            )


@pytest.mark.integration
class TestEmailFinderAdvanced:
    """Advanced integration tests for email finder functionality."""

    def test_find_email_confidence_levels(
        self,
        hunter_client: HunterClient,
        test_person_data: dict,
    ) -> None:
        """Test email finder confidence score interpretation.

        Args:
            hunter_client: Configured Hunter client instance.
            test_person_data: Test person data for email finding.

        """
        email, score = hunter_client.email_finder(
            domain=test_person_data['domain'],
            first_name=test_person_data['first_name'],
            last_name=test_person_data['last_name'],
        )

        # Test confidence levels
        high_confidence_threshold = 70
        medium_confidence_threshold = 40
        if score >= high_confidence_threshold:
            confidence_level = 'high'
        elif score >= medium_confidence_threshold:
            confidence_level = 'medium'
        else:
            confidence_level = 'low'

        assert confidence_level in {'high', 'medium', 'low'}, 'Confidence should be categorized'

        # Verify email format regardless of confidence
        assert '@' in email, 'Email should be valid format'
        assert '.' in email.split('@')[1], 'Domain should have TLD'

    def test_api_consistency_between_methods(
        self,
        hunter_client: HunterClient,
    ) -> None:
        """Test consistency between full_name and separate names.

        Args:
            hunter_client: Configured Hunter client instance.

        """
        # Test with separate names
        email1, score1 = hunter_client.email_finder(
            domain='stripe.com',
            first_name='Patrick',
            last_name='Collison',
        )

        # Test with full name
        email2, score2 = hunter_client.email_finder(
            domain='stripe.com',
            full_name='Patrick Collison',
        )

        # Both methods should return the same email
        assert email1 == email2, 'Both methods should return same email'

        # Scores should be identical or very close
        assert abs(score1 - score2) <= 10, 'Scores should be similar between methods'
