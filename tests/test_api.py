import json
from contract_management.api.app import handle_api_request
from contract_management.models.contract import Contract, ContractStatus

def test_api_health_check():
    status, res = handle_api_request("GET", "/api/health")
    assert status == 200
    assert res["status"] == "healthy"

def test_api_create_and_fetch_contract(memory_db):
    payload = {
        "title": "API Cloud Hosting",
        "contract_number": "API-TEST-001",
        "counterparty_name": "HostWorks Inc",
        "total_value": 75000.0,
        "effective_date": "2026-01-01",
        "expiration_date": "2027-01-01"
    }
    status, res = handle_api_request("POST", "/api/contracts", body=json.dumps(payload), conn=memory_db)
    assert status == 201
    assert res["contract"]["contract_number"] == "API-TEST-001"
