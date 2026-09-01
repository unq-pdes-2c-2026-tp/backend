from rest_framework.test import APIClient


def post(url, data, fmt="json", user=None):
    client = APIClient()
    if user:
        client.force_authenticate(user)
    response = client.post(url, data, format=fmt)
    return response


def delete(url, user=None):
    client = APIClient()
    if user:
        client.force_authenticate(user)
    response = client.delete(url)
    return response


def get(url, params=None):
    params = params or {}

    client = APIClient()
    full_url = url
    if params:
        full_url += "?" + "&".join([f"{key}={value}" for key, value in params.items()])
    response = client.get(full_url)
    return response
