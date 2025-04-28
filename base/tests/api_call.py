import pytest


@pytest.fixture
def base_api_client(api_client):
    """Fixture for Season API client with the base URL."""

    def _request(method, base_url, endpoint="", data=None, params=None, id=None):
        """Helper function to make API requests."""

        # Construct the URL properly
        if id:
            url = f"{base_url}/{id}"
        else:
            url = f"{base_url}/{endpoint}".rstrip("/")

        print(url, "url --->")

        # Define a mapping for supported HTTP methods
        methods = {
            "get": api_client.get,
            "post": api_client.post,
            "put": api_client.put,
            "patch": api_client.patch,
            "delete": api_client.delete,
        }

        method = method.lower()
        if method not in methods:
            raise ValueError(f"Unsupported HTTP method: {method}")

        # Call the appropriate method
        return methods[method](url, data=data, params=params, format="json")

    return _request
