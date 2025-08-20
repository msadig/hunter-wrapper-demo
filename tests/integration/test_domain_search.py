"""Integration tests for HunterClient.domain_search method."""

import pytest
import requests

from hunter_wrapper.client import HunterClient
from hunter_wrapper.exceptions import MissingCompanyError


@pytest.mark.integration
class TestDomainSearchBasic:
    """Basic integration tests for domain search functionality."""

    def test_search_by_domain(self, hunter_client: HunterClient, test_domain: str) -> None:
        """Test searching emails by domain.

        This test verifies that:
        1. The API accepts domain search requests
        2. Returns expected data structure
        3. Provides email addresses for the domain

        Args:
            hunter_client: Configured Hunter client instance.
            test_domain: Test domain to search.

        """
        search_response = hunter_client.domain_search(domain=test_domain)
        self._verify_domain_response_structure(search_response, test_domain)

        # If emails are found, verify their structure
        if search_response['emails']:
            self._verify_email_structure(search_response['emails'][0], test_domain)

    def test_search_by_company_name(self, hunter_client: HunterClient, test_company: str) -> None:
        """Test searching emails by company name.

        Args:
            hunter_client: Configured Hunter client instance.
            test_company: Test company name to search.

        """
        company_response = hunter_client.domain_search(company=test_company)

        assert isinstance(company_response, dict), 'Response should be a dictionary'

        # Should have found a domain for the company
        assert 'domain' in company_response, 'Response should include domain'

        # Should have email list (even if empty)
        assert 'emails' in company_response, 'Response should include emails list'
        assert isinstance(company_response['emails'], list), 'Emails should be a list'

    def _verify_domain_response_structure(self, response: dict, test_domain: str) -> None:
        """Verify domain search response structure.

        Args:
            response: Response dictionary from API.
            test_domain: Expected domain in response.

        """
        # Verify the response structure
        assert isinstance(response, dict), 'Response should be a dictionary'

        # Check for essential fields in the response
        expected_fields = {
            'domain',
            'disposable',
            'webmail',
            'accept_all',
            'pattern',
            'organization',
            'emails',
        }

        missing_fields = expected_fields - set(response.keys())
        error_msg = 'Missing expected fields: {0}'.format(missing_fields)
        assert not missing_fields, error_msg

        # Verify domain in response
        assert response['domain'] == test_domain, 'Response domain should match requested domain'

        # Verify emails field is a list
        assert isinstance(response['emails'], list), 'Emails should be a list'

    def _verify_email_structure(self, email_entry: dict, test_domain: str) -> None:
        """Verify email entry structure.

        Args:
            email_entry: Email dictionary from response.
            test_domain: Expected domain in email.

        """
        email_fields = {
            'value',
            'type',
            'confidence',
            'sources',
            'first_name',
            'last_name',
            'position',
            'seniority',
            'department',
            'linkedin',
            'twitter',
            'phone_number',
            'verification',
        }

        missing_email_fields = email_fields - set(email_entry.keys())
        email_error_msg = 'Missing email fields: {0}'.format(missing_email_fields)
        assert not missing_email_fields, email_error_msg

        # Verify email belongs to the domain
        domain_msg = 'Email should belong to {0}'.format(test_domain)
        assert test_domain in email_entry['value'], domain_msg


@pytest.mark.integration
class TestDomainSearchPagination:
    """Integration tests for domain search pagination."""

    def test_search_with_limit(self, hunter_client: HunterClient, test_domain: str) -> None:
        """Test domain search with result limit.

        Args:
            hunter_client: Configured Hunter client instance.
            test_domain: Test domain to search.

        """
        limit_value = 5
        paginated_response = hunter_client.domain_search(domain=test_domain, limit=limit_value)

        assert isinstance(paginated_response, dict), 'Response should be a dictionary'
        assert 'emails' in paginated_response, 'Response should include emails'

        # Check that limit is respected
        if paginated_response['emails']:
            limit_msg = 'Should return at most {0} emails'.format(limit_value)
            assert len(paginated_response['emails']) <= limit_value, limit_msg

    def test_search_with_offset(self, hunter_client: HunterClient, test_domain: str) -> None:
        """Test domain search with offset for pagination.

        Args:
            hunter_client: Configured Hunter client instance.
            test_domain: Test domain to search.

        """
        page_size = 2
        # Get first page
        first_page = hunter_client.domain_search(domain=test_domain, limit=page_size, offset=0)

        # Get second page
        second_page = hunter_client.domain_search(domain=test_domain, limit=page_size, offset=page_size)

        assert isinstance(first_page, dict), 'First response should be a dictionary'
        assert isinstance(second_page, dict), 'Second response should be a dictionary'

        # If there are enough results, emails should be different
        if first_page.get('emails') and second_page.get('emails'):
            first_emails = {email['value'] for email in first_page['emails']}
            second_emails = {email['value'] for email in second_page['emails']}

            # Pages should have different emails (if enough exist)
            if first_emails and second_emails:
                assert first_emails != second_emails, 'Different pages should have different emails'


@pytest.mark.integration
class TestDomainSearchFilters:
    """Integration tests for domain search filters."""

    def test_search_with_seniority_filter(self, hunter_client: HunterClient, test_domain: str) -> None:
        """Test domain search with seniority filter.

        Args:
            hunter_client: Configured Hunter client instance.
            test_domain: Test domain to search.

        """
        seniority_response = hunter_client.domain_search(
            domain=test_domain,
            seniority='executive',
        )

        assert isinstance(seniority_response, dict), 'Response should be a dictionary'
        assert 'emails' in seniority_response, 'Response should include emails'

        # If emails found with seniority filter, verify they match
        if seniority_response['emails']:
            for email in seniority_response['emails']:
                if email.get('seniority'):
                    # API might return executives in various forms
                    seniority = email['seniority'].lower()
                    is_executive = 'executive' in seniority
                    assert is_executive, 'Filtered emails should match seniority'

    def test_search_with_department_filter(self, hunter_client: HunterClient, test_domain: str) -> None:
        """Test domain search with department filter.

        Args:
            hunter_client: Configured Hunter client instance.
            test_domain: Test domain to search.

        """
        department_response = hunter_client.domain_search(
            domain=test_domain,
            department='it',
        )

        assert isinstance(department_response, dict), 'Response should be a dictionary'
        assert 'emails' in department_response, 'Response should include emails'

    def test_search_with_emails_type_filter(self, hunter_client: HunterClient, test_domain: str) -> None:
        """Test domain search with email type filter.

        Args:
            hunter_client: Configured Hunter client instance.
            test_domain: Test domain to search.

        """
        type_response = hunter_client.domain_search(
            domain=test_domain,
            emails_type='personal',
        )

        assert isinstance(type_response, dict), 'Response should be a dictionary'
        assert 'emails' in type_response, 'Response should include emails'

        # If emails found with type filter, verify they match
        if type_response['emails']:
            for email in type_response['emails']:
                assert email.get('type') == 'personal', 'Filtered emails should be personal type'


@pytest.mark.integration
class TestDomainSearchMetadata:
    """Integration tests for domain search metadata and response formats."""

    def test_search_with_raw_response(self, hunter_client: HunterClient, test_domain: str) -> None:
        """Test domain search with raw response flag.

        Args:
            hunter_client: Configured Hunter client instance.
            test_domain: Test domain to search.

        """
        raw_response = hunter_client.domain_search(domain=test_domain, raw=True)

        # When raw=True, should return Response object
        assert isinstance(raw_response, requests.Response), 'Raw response should be requests.Response'
        status_code = 200
        assert raw_response.status_code == status_code, 'Should get successful response'

        # Parse JSON to verify structure
        json_data = raw_response.json()
        assert 'data' in json_data, 'Response should have data field'
        assert 'meta' in json_data, 'Response should have meta field'

    def test_api_response_metadata(self, hunter_client: HunterClient, test_domain: str) -> None:
        """Test that API provides proper metadata.

        Args:
            hunter_client: Configured Hunter client instance.
            test_domain: Test domain to search.

        """
        json_data = hunter_client.domain_search(domain=test_domain, raw=True).json()
        assert 'meta' in json_data, 'Response should have meta field'

        # Meta should contain results count and params info
        expected_meta_fields = {'results', 'limit', 'offset', 'params'}
        missing_meta = expected_meta_fields - set(json_data['meta'].keys())
        assert not missing_meta, 'Missing meta fields: {0}'.format(missing_meta)


@pytest.mark.integration
class TestDomainSearchErrors:
    """Integration tests for domain search error handling."""

    def test_search_missing_company_error(self, hunter_client: HunterClient) -> None:
        """Test that missing both domain and company raises error.

        Args:
            hunter_client: Configured Hunter client instance.

        """
        with pytest.raises(MissingCompanyError, match='domain name or a company name'):
            hunter_client.domain_search()


@pytest.mark.integration
class TestDomainSearchCombined:
    """Integration tests for combined domain search parameters."""

    def test_search_with_all_parameters(self, hunter_client: HunterClient, test_domain: str) -> None:
        """Test domain search with multiple parameters combined.

        Args:
            hunter_client: Configured Hunter client instance.
            test_domain: Test domain to search.

        """
        max_emails = 3
        combined_response = hunter_client.domain_search(
            domain=test_domain,
            limit=max_emails,
            offset=0,
            seniority='senior',
            department='management',
            emails_type='personal',
        )

        assert isinstance(combined_response, dict), 'Response should be a dictionary'
        assert 'emails' in combined_response, 'Response should include emails'

        # Verify limit is respected
        if combined_response['emails']:
            assert len(combined_response['emails']) <= max_emails, 'Should respect limit parameter'
