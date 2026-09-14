from rest_framework.test import APIClient


def post(url, data, fmt="json", user=None, token=None, **kwargs):
    client = _get_client(user, token)
    response = client.post(url, data, format=fmt, **kwargs)
    return response


def delete(url, user=None, token=None):
    client = _get_client(user, token)
    response = client.delete(url)
    return response


def patch(url, data, fmt="json", user=None, token=None):
    client = _get_client(user, token)
    response = client.patch(url, data=data, format=fmt)
    return response


def put(url, data, fmt="json", user=None, token=None):
    client = _get_client(user, token)
    response = client.put(url, data=data, format=fmt)
    return response


def get(url, params=None, user=None, token=None):
    params = params or {}

    client = _get_client(user, token)
    full_url = url
    if params:
        full_url += "?" + "&".join([f"{key}={value}" for key, value in params.items()])
    response = client.get(full_url)
    return response


def _get_client(user, token) -> APIClient:
    client = APIClient()
    if user:
        client.force_authenticate(user, token)
    return client
