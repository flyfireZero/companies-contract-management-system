import json
from typing import Dict, Any, Tuple
from contract_management.db.connection import get_db
from contract_management.db.repositories.contract_repo import ContractRepository
from contract_management.db.repositories.company_repo import CompanyRepository
from contract_management.lifecycle.expiry_engine import ExpiryEngine
from contract_management.lifecycle.state_machine import ContractStateMachine
from contract_management.analytics.stats import PortfolioAnalytics
from contract_management.models.contract import Contract, ContractStatus, ContractType

def handle_api_request(method: str, path: str, body: Optional[str] = None, db_path=None) -> Tuple[int, Dict[str, Any]]:
    """
    Pure Python REST router handling API requests.
    Supports endpoints:
    GET  /api/health
    GET  /api/contracts
    POST /api/contracts
    GET  /api/contracts/{id}
    POST /api/contracts/{id}/transition
    GET  /api/analytics
    GET  /api/expiry/scan
    """
    from contract_management.config import DATABASE_PATH
    actual_db = db_path or DATABASE_PATH
    conn = get_db(actual_db)
    contract_repo = ContractRepository(conn)
    company_repo = CompanyRepository(conn)

    # 1. Health check
    if method == "GET" and path == "/api/health":
        return 200, {"status": "healthy", "service": "CCMS Contract API", "version": "0.1.0"}

    # 2. List contracts
    if method == "GET" and path == "/api/contracts":
        contracts = contract_repo.list_contracts()
        return 200, {"success": True, "count": len(contracts), "contracts": [c.to_dict() for c in contracts]}

    # 3. Create contract
    if method == "POST" and path == "/api/contracts":
        if not body:
            return 400, {"success": False, "error": "Request body missing"}
        payload = json.loads(body)
        c = Contract(
            title=payload["title"],
            contract_number=payload["contract_number"],
            counterparty_name=payload["counterparty_name"],
            contract_type=ContractType(payload.get("contract_type", "MSA")),
            total_value=float(payload.get("total_value", 0.0)),
            annual_value=float(payload.get("annual_value", 0.0)),
            effective_date=payload.get("effective_date"),
            expiration_date=payload.get("expiration_date"),
            auto_renew=bool(payload.get("auto_renew", False))
        )
        saved = contract_repo.create(c)
        return 201, {"success": True, "contract": saved.to_dict()}

    # 4. Get single contract
    if method == "GET" and path.startswith("/api/contracts/"):
        parts = path.strip("/").split("/")
        if len(parts) == 3 and parts[2].isdigit():
            cid = int(parts[2])
            c = contract_repo.get_by_id(cid)
            if not c:
                return 404, {"success": False, "error": "Contract not found"}
            clauses = contract_repo.get_clauses(cid)
            return 200, {
                "success": True,
                "contract": c.to_dict(),
                "clauses": [cl.to_dict() for cl in clauses]
            }

    # 5. Transition status
    if method == "POST" and path.startswith("/api/contracts/") and path.endswith("/transition"):
        parts = path.strip("/").split("/")
        cid = int(parts[2])
        c = contract_repo.get_by_id(cid)
        if not c:
            return 404, {"success": False, "error": "Contract not found"}
        payload = json.loads(body or "{}")
        target_status = ContractStatus(payload["target_status"])
        ContractStateMachine.transition(c, target_status)
        contract_repo.update_status(cid, target_status)
        return 200, {"success": True, "new_status": target_status.value}

    # 6. Analytics
    if method == "GET" and path == "/api/analytics":
        contracts = contract_repo.list_contracts()
        summary = PortfolioAnalytics.compute_summary(contracts)
        return 200, {"success": True, "analytics": summary.__dict__}

    # 7. Expiry scan
    if method == "GET" and path == "/api/expiry/scan":
        contracts = contract_repo.list_contracts()
        alerts = ExpiryEngine().scan_all(contracts)
        return 200, {"success": True, "alerts": [a.__dict__ for a in alerts]}

    return 404, {"success": False, "error": f"Endpoint not found: {method} {path}"}

def create_app():
    return handle_api_request
