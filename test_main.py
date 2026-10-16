from fastapi.testclient import TestClient
from main import app
client=TestClient(app)
def test_health():
    r=client.get("/api/health");assert r.status_code==200 and r.json()["status"]=="ok"
def test_run():
    r=client.post("/api/run",json={"request":"Summarize this urgent lead and prepare a CRM follow-up.","provider":"openai","workflow_type":"crm","approval_required":True})
    assert r.status_code==200 and r.json()["status"]=="awaiting_approval"
def test_approval():
    d=client.post("/api/run",json={"request":"Create a support task for this customer issue.","provider":"claude","workflow_type":"support","approval_required":True}).json()
    r=client.post(f"/api/approve/{d['run_id']}");assert r.status_code==200 and r.json()["status"]=="completed"
