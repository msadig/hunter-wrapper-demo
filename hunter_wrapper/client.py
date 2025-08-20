"""Hunter.io API client implementation.

This module provides the main client class for interacting with Hunter.io API.
"""

import requests

from hunter_wrapper.exceptions import HunterAPIError


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
