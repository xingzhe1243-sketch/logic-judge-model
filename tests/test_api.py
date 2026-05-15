"""API 测试 — 验证 FastAPI 端点"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from api_server import app

client = TestClient(app)

SAMPLE_TEXT = "因为所有人都应该享有自由，所以政府不应限制言论自由。"


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["version"] == "2.0.0"
    print("[OK] test_health")


def test_modules():
    resp = client.get("/modules")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 9
    names = [m["name"] for m in data]
    assert "formal_logic" in names
    assert "critical_inquiry" in names
    print("[OK] test_modules")


def test_analyze():
    resp = client.post("/analyze", json={"text": SAMPLE_TEXT})
    assert resp.status_code == 200
    data = resp.json()
    assert "input" in data
    assert "modules" in data
    assert "synthesis" in data
    assert data["input"] == SAMPLE_TEXT
    print("[OK] test_analyze")


def test_analyze_with_modules():
    resp = client.post("/analyze", json={
        "text": SAMPLE_TEXT,
        "modules": ["formal_logic", "critical_inquiry"]
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "formal_logic" in data["modules"]
    assert data["modules"]["formal_logic"] != {}
    assert "critical_inquiry" in data["modules"]
    print("[OK] test_analyze_with_modules")


def test_analyze_empty_text():
    resp = client.post("/analyze", json={"text": ""})
    assert resp.status_code == 422
    print("[OK] test_analyze_empty_text")


def test_batch_analyze():
    resp = client.post("/analyze/batch", json={
        "texts": [SAMPLE_TEXT, "所有人都知道这是对的。"]
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    assert len(data["results"]) == 2
    for r in data["results"]:
        assert "input" in r
    print("[OK] test_batch_analyze")


def test_batch_with_modules():
    texts = ["文本一", "文本二"]
    resp = client.post("/analyze/batch", json={
        "texts": texts,
        "modules": ["simple_logic"]
    })
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["results"]) == 2
    for r in data["results"]:
        assert "simple_logic" in r["modules"]
    print("[OK] test_batch_with_modules")


if __name__ == "__main__":
    test_health()
    test_modules()
    test_analyze()
    test_analyze_with_modules()
    test_analyze_empty_text()
    test_batch_analyze()
    test_batch_with_modules()
    print("\n" + "=" * 40)
    print("所有API测试通过!")
    print("=" * 40)
