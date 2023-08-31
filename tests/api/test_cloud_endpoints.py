import pytest
from httpx import AsyncClient
import os

SERVICE_URL = os.environ.get("SERVICE_URL")

test_params = {}


@pytest.mark.asyncio
async def test_root_is_up():
    async with AsyncClient(base_url=SERVICE_URL, timeout=10) as ac:
        response = await ac.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_root_returns_greeting():
    async with AsyncClient(base_url=SERVICE_URL, timeout=10) as ac:
        response = await ac.get("/")
    assert response.json() == {"greeting": "Hello"}


@pytest.mark.asyncio
async def test_predict_is_up():
    async with AsyncClient(base_url=SERVICE_URL, timeout=10) as ac:
        response = await ac.get("/predict", params=test_params)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_predict_is_dict():
    async with AsyncClient(base_url=SERVICE_URL, timeout=10) as ac:
        response = await ac.get("/predict", params=test_params)
    assert isinstance(response.json(), dict)
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_predict_has_key():
    async with AsyncClient(base_url=SERVICE_URL, timeout=10) as ac:
        response = await ac.get("/predict", params=test_params)
    assert response.json().get("classe", False)


@pytest.mark.asyncio
async def test_cloud_api_predict():
    async with AsyncClient(base_url=SERVICE_URL, timeout=10) as ac:
        response = await ac.get("/predict", params=test_params)
    assert isinstance(response.json().get("classe"), str)
