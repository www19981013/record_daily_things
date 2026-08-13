def test_create_entry(client):
    resp = client.post("/entries", json={"content": "写完周报"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == 1
    assert body["content"] == "写完周报"


def test_list_entries(client):
    client.post("/entries", json={"content": "第一件事"})
    client.post("/entries", json={"content": "第二件事"})
    resp = client.get("/entries")
    assert resp.status_code == 200
    contents = [e["content"] for e in resp.json()]
    assert contents == ["第二件事", "第一件事"]  # 按时间倒序


def test_delete_entry(client):
    created = client.post("/entries", json={"content": "要删除的"}).json()
    resp = client.delete(f"/entries/{created['id']}")
    assert resp.status_code == 204
    assert client.get("/entries").json() == []


def test_delete_missing_entry_returns_404(client):
    resp = client.delete("/entries/999")
    assert resp.status_code == 404
