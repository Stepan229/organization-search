"""API tests: auth, organization by id, search by activity (subtree), by name, geo, and activity level constraint."""
import os
import uuid

import pytest

from tests.conftest import API_KEY_HEADERS

# Tests that need seeded data require PostgreSQL (SQLite has UUID serialization issues with our models)
REQUIRES_PG = os.environ.get("TEST_DATABASE_URL", "").startswith("postgresql")


def test_401_without_api_key(client):
    response = client.get("/api/v1/buildings")
    assert response.status_code == 401
    assert "detail" in response.json()


def test_401_wrong_api_key(client):
    response = client.get("/api/v1/buildings", headers={"X-API-Key": "wrong"})
    assert response.status_code == 401


def test_get_organization_not_found(client):
    response = client.get(
        f"/api/v1/organizations/{uuid.uuid4()}",
        headers=API_KEY_HEADERS,
    )
    assert response.status_code == 404
    assert "detail" in response.json()


@pytest.mark.skipif(not REQUIRES_PG, reason="Seeded data tests require PostgreSQL (TEST_DATABASE_URL)")
def test_get_organization_ok(client, seed_data):
    org_id = seed_data["org_id"]
    response = client.get(f"/api/v1/organizations/{org_id}", headers=API_KEY_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(org_id)
    assert "Рога и Копыта" in data["name"]
    assert data["building"]["address"]
    assert len(data["phones"]) >= 1
    assert len(data["activities"]) >= 1


@pytest.mark.skipif(not REQUIRES_PG, reason="Seeded data tests require PostgreSQL")
def test_list_buildings(client, seed_data):
    response = client.get("/api/v1/buildings", headers=API_KEY_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


@pytest.mark.skipif(not REQUIRES_PG, reason="Seeded data tests require PostgreSQL")
def test_list_organizations_in_building(client, seed_data):
    building_id = seed_data["building_id"]
    response = client.get(
        f"/api/v1/buildings/{building_id}/organizations",
        headers=API_KEY_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any("Рога и Копыта" in o["name"] for o in data)


@pytest.mark.skipif(not REQUIRES_PG, reason="Seeded data tests require PostgreSQL")
def test_search_organizations_by_name(client, seed_data):
    response = client.get(
        "/api/v1/search/organizations/by-name",
        params={"q": "Рога"},
        headers=API_KEY_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any("Рога" in o["name"] for o in data)


@pytest.mark.skipif(not REQUIRES_PG, reason="Seeded data tests require PostgreSQL")
def test_search_organizations_by_activity_name_with_subtree(client, seed_data):
    """Search by activity 'Еда' (root) should return orgs in Еда, Мясная продукция, Молочная продукция."""
    response = client.get(
        "/api/v1/search/organizations/by-activity",
        params={"activity_name": "Еда"},
        headers=API_KEY_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    names = [o["name"] for o in data]
    assert any("Рога" in n for n in names) or any("Мясной" in n for n in names)


@pytest.mark.skipif(not REQUIRES_PG, reason="Seeded data tests require PostgreSQL")
def test_activities_organizations_include_subtree(client, seed_data):
    activity_id = seed_data["activity_id"]
    response = client.get(
        f"/api/v1/activities/{activity_id}/organizations",
        params={"include_subtree": True},
        headers=API_KEY_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_search_geo_radius_bad_request(client):
    # radius_m < 0 is rejected by query validation (422) or by service (400)
    response = client.get(
        "/api/v1/search/organizations/geo/radius",
        params={"lat": 55.75, "lon": 37.62, "radius_m": -100},
        headers=API_KEY_HEADERS,
    )
    assert response.status_code in (400, 422)


@pytest.mark.skipif(not REQUIRES_PG, reason="Seeded data tests require PostgreSQL")
def test_search_geo_box(client, seed_data):
    response = client.get(
        "/api/v1/search/organizations/geo/box",
        params={
            "lat_min": 55.0,
            "lat_max": 56.0,
            "lon_min": 37.0,
            "lon_max": 38.0,
        },
        headers=API_KEY_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_search_by_name_empty_query(client):
    response = client.get(
        "/api/v1/search/organizations/by-name",
        params={"q": ""},
        headers=API_KEY_HEADERS,
    )
    assert response.status_code == 422  # validation error for min_length=1
