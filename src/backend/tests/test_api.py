import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from app.main import app, settings

client = TestClient(app)

FILES_DIR = Path(__file__).resolve().parent / "assets"


def test_health_endpoint():
    url = url = f"{settings.API_V1_STR}/health"
    response = client.get(url=url)
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}


def test_detect_endpoint():
    url = url = f"{settings.API_V1_STR}/detect"
    files = {"file": open(FILES_DIR / "pedestrians.jpg", "rb")}
    response = client.post(url=url, files=files)
    assert response.status_code == 200
    response_dict = response.json()
    assert "results" in response_dict.keys()
    assert "inference_time" in response_dict.keys()


def test_pedestrian_detection():
    url = url = f"{settings.API_V1_STR}/detect"
    files = {"file": open(FILES_DIR / "pedestrians.jpg", "rb")}
    response = client.post(url=url, files=files)
    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) == 3
    num_pedestrians = sum(
        [1 for det in results if det["label"] == "pedestrian"]
    )
    assert num_pedestrians == 3


def test_rider_detection():
    url = url = f"{settings.API_V1_STR}/detect"
    files = {"file": open(FILES_DIR / "riders.png", "rb")}
    response = client.post(url=url, files=files)
    assert response.status_code == 200
    results = response.json()["results"]
    num_riders = sum([1 for det in results if det["label"] == "rider"])
    assert num_riders >= 5
