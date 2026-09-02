from rest_framework.test import APIClient


def post(url, data, fmt="json", user=None, **kwargs):
    client = _get_client(user)
    response = client.post(url, data, format=fmt, **kwargs)
    return response


def delete(url, user=None):
    client = _get_client(user)
    response = client.delete(url)
    return response


def patch(url, data, fmt="json", user=None):
    client = _get_client(user)
    response = client.patch(url, data=data, format=fmt)
    return response


def put(url, data, fmt="json", user=None):
    client = _get_client(user)
    response = client.put(url, data=data, format=fmt)
    return response


def get(url, params=None, user=None):
    params = params or {}

    client = _get_client(user)
    full_url = url
    if params:
        full_url += "?" + "&".join([f"{key}={value}" for key, value in params.items()])
    response = client.get(full_url)
    return response


def _get_client(user) -> APIClient:
    client = APIClient()
    if user:
        client.force_authenticate(user)
    return client
