from fastapi.testclient import TestClient


def test_auth_required(client: TestClient) -> None:
    response = client.post("/api/v1/organizations/search", json={"name": "ООО"})
    assert response.status_code == 401


def test_get_organization_by_id_returns_activities(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.get("/api/v1/organizations/1", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == 1
    assert "activities" in payload
    assert isinstance(payload["activities"], list)


def test_list_organizations_by_building(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/organizations/by-building",
        json={"building_id": 1, "offset": 0, "limit": 20},
        headers=auth_headers,
    )
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)


def test_search_by_name(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/organizations/search",
        json={"name": "ООО", "offset": 0, "limit": 20},
        headers=auth_headers,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert all("ООО" in item["name"] for item in payload)


def test_search_by_activity_id_with_descendants(client: TestClient, auth_headers: dict[str, str]) -> None:
    no_desc = client.post(
        "/api/v1/organizations/by-activity-id",
        json={"activity_id": 1, "include_descendants": False},
        headers=auth_headers,
    )
    with_desc = client.post(
        "/api/v1/organizations/by-activity-id",
        json={"activity_id": 1, "include_descendants": True},
        headers=auth_headers,
    )
    assert no_desc.status_code == 200
    assert with_desc.status_code == 200
    assert len(with_desc.json()) >= len(no_desc.json())


def test_search_by_activity_name_with_depth_limit(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/organizations/by-activity-name",
        json={"name": "Еда"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload


def test_geo_radius_returns_two_lists(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/organizations/geo/radius",
        json={
            "latitude": 55.75,
            "longitude": 37.61,
            "radius_m": 5000,
            "offset": 0,
            "limit": 20,
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    payload = response.json()
    assert "organizations" in payload
    assert "buildings" in payload


def test_geo_bbox_returns_two_lists(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/organizations/geo/bbox",
        json={
            "min_latitude": 55.70,
            "min_longitude": 37.50,
            "max_latitude": 55.80,
            "max_longitude": 37.70,
            "offset": 0,
            "limit": 20,
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    payload = response.json()
    assert "organizations" in payload
    assert "buildings" in payload
