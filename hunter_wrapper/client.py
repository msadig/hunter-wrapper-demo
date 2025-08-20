"""Hunter.io API client implementation.

This module provides the main client class for interacting with Hunter.io API.
"""

import requests

from hunter_wrapper.exceptions import HunterAPIError, MissingCompanyError, MissingNameError


class HunterClient:
    """Client for interacting with the Hunter.io API.

    For documentation, visit: https://hunter.io/api-documentation/v2
    """

    def __init__(self, api_key: str) -> None:
        """Initialize the HunterClient.

        Args:
            api_key: The API key for Hunter.io authentication.

        """
        self.api_key = api_key
        self.base_params = {'api_key': api_key}
        self.base_endpoint = 'https://api.hunter.io/v2/{endpoint}'

    def email_verifier(self, email: str, raw: bool = False) -> dict:
        """Verify the deliverability of a given email address.

        Args:
            email: The email address to check.
            raw: If True, returns the entire response instead of just the 'data'.

        Returns:
            Full payload of the query as a dict.

        """
        query_params = {'email': email, 'api_key': self.api_key}
        endpoint = self.base_endpoint.format(endpoint='email-verifier')
        return self._query_hunter(
            endpoint,
            query_params,
            raw=raw,
        )

    def domain_search(
        self,
        domain: str | None = None,
        company: str | None = None,
        raw: bool = False,
        **kwargs,
    ) -> dict:
        """Return all the email addresses found for a given domain.

        Args:
            domain: The domain on which to search for emails. Must be defined if company is not.
            company: The name of the company on which to search for emails. Must be defined if domain is not.
            raw: If True, returns the entire response instead of just the 'data'.

        Returns:
            Full payload of the query as a dict, with email addresses found.

        Raises:
            MissingCompanyError: If neither domain nor company is provided.

        """
        if domain:
            query_parameters = {'domain': domain, 'api_key': self.api_key}
        elif company:
            query_parameters = {'company': company, 'api_key': self.api_key}
        else:
            raise MissingCompanyError(
                'You must supply at least a domain name or a company name',
            )

        # Add optional parameters from kwargs
        self._add_optional_search_params(query_parameters, kwargs)

        endpoint = self.base_endpoint.format(endpoint='domain-search')

        return self._query_hunter(endpoint, query_parameters, raw=raw)

    def email_finder(
        self,
        domain: str | None = None,
        company: str | None = None,
        raw: bool = False,
        **name_params,
    ) -> dict | tuple[str, int]:
        """Find the email address of a person given its name and company's domain.

        Args:
            domain: The domain of the company where the person works. Must be defined if company is not.
            company: The name of the company where the person works. Must be defined if domain is not.
            raw: If True, returns the entire response instead of just email and score.

        Returns:
            If raw is True: Full API response as dict.
            If raw is False: Tuple of (email, score).

        """
        query_parameters = self.base_params.copy()

        # Validate and add company/domain parameters
        if not domain and not company:
            raise MissingCompanyError(
                'You must supply at least a domain name or a company name',
            )
        if domain:
            query_parameters['domain'] = domain
        elif company:
            query_parameters['company'] = company

        # Validate and add name parameters
        self._add_name_params(query_parameters, name_params)

        endpoint = self.base_endpoint.format(endpoint='email-finder')

        response = self._query_hunter(endpoint, query_parameters, raw=raw)
        if raw:
            return response

        email = response['email']
        score = response['score']

        return email, score

    def _add_name_params(
        self,
        query_parameters: dict,
        name_params: dict,
    ) -> None:
        """Add name parameters to the query.

        Args:
            query_parameters: The query parameters dict to update.
            name_params: Dictionary containing name-related parameters.

        Raises:
            MissingNameError: If name information is insufficient.

        """
        first_name = name_params.get('first_name')
        last_name = name_params.get('last_name')
        full_name = name_params.get('full_name')

        has_both_names = bool(first_name and last_name)

        if not full_name and not has_both_names:
            raise MissingNameError(
                'You must supply a first name AND a last name OR a full name',
            )

        if has_both_names:
            query_parameters['first_name'] = first_name
            query_parameters['last_name'] = last_name
        elif full_name:
            query_parameters['full_name'] = full_name

    def _add_optional_search_params(
        self,
        query_parameters: dict,
        kwargs: dict,
    ) -> None:
        """Add optional search parameters to the query.

        Args:
            query_parameters: The query parameters dict to update.
            kwargs: Dictionary containing optional parameters.

        """
        optional_params = {
            'limit': 'limit',
            'offset': 'offset',
            'seniority': 'seniority',
            'department': 'department',
            'emails_type': 'type',
        }

        for key, api_key in optional_params.items():
            param_value = kwargs.get(key, None)
            if param_value is not None:
                query_parameters[api_key] = param_value

    def _query_hunter(
        self,
        endpoint: str,
        query_params: dict,
        request_type: str = 'get',
        raw: bool = False,
    ) -> dict:
        """Make a request to the Hunter.io API.

        Args:
            endpoint: The API endpoint URL.
            query_params: Query parameters for the request.
            request_type: HTTP method to use.
            raw: If True, return the raw response.

        Returns:
            API response data or raw response.

        Raises:
            HunterAPIError: If the API returns an error.

        """
        request_kwargs = {'params': query_params}
        res = getattr(requests, request_type)(endpoint, **request_kwargs)
        res.raise_for_status()

        if raw:
            return res

        try:
            response_data = res.json()['data']
        except KeyError:
            error_message = str(res.json())
            raise HunterAPIError(error_message)

        return response_data
