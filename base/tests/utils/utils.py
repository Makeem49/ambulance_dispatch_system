import logging
import pytest
from django.urls import reverse
from rest_framework import status


logger = logging.getLogger(__name__)


@pytest.fixture
def data():
    def _data(data):
        return data

    return _data


@pytest.fixture
def create(api_client):
    def _create(view_name, data):
        url = reverse(view_name)
        response = api_client.post(url, data, format="json")
        logger.info(f"Response Data: {response.json()}")
        return response.json()

    return _create


@pytest.fixture
def list(api_client):
    def _list(view_name):
        url = reverse(view_name)
        response = api_client.get(url, format="json")
        logger.info(f"Response Data: {response.json()}")
        return response.json()

    return _list


@pytest.fixture
def manager_operator(db):
    """Fixture to create an instance using the manager."""

    def _season(manager, method, *args, **kwargs):
        instance, error, status_code = getattr(manager, method)(*args, **kwargs)
        return instance, error, status_code  # Return the created instance

    return _season
