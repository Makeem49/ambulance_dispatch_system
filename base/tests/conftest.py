import pytest

from rest_framework.test import APIClient


@pytest.fixture(scope="class")
def api_client() -> APIClient:
    """
    Fixture to provide an API client
    :return: APIClient
    """
    yield APIClient()


@pytest.fixture(scope="class")
def class_db(db):
    # Custom setup if needed
    yield
