import argparse
import sys
import json
from pathlib import Path
from contract_management.db.connection import get_db, DatabaseEngine
from contract_management.db.repositories.contract_repo import ContractRepository
from contract_management.db.repositories.company_repo import CompanyRepository
from contract_management.ingestion.parser import DocumentParser
from contract_management.ingestion.storage import DocumentStorage
from contract_management.ai.clause_extractor import ClauseExtractor
from contract_management.ai.risk_analyzer import RiskAnalyzer
from contract_management.ai.summarizer import ContractSummarizer
from contract_management.lifecycle.expiry_engine import ExpiryEngine
from contract_management.lifecycle.state_machine import ContractStateMachine
from contract_management.analytics.stats import PortfolioAnalytics
from contract_management.analytics.exporter import ReportExporter
from contract_management.models.contract import Contract, ContractStatus, ContractType, Priority
from contract_management.models.clause import Clause

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="contractctl",
        description="Companies Contract Management System (CCMS) CLI"
    )
    sub = parser.add_subparsers(dest="subcommand", required=True)

    # init-db
    p_init = sub.add_parser("init-db", help="Initialize or reset SQLite schema")

    # list
    p_list = sub.add_parser("list", help="List contracts in the system")
    p_list.add_argument("--status", choices=[s.value for s in ContractStatus], help="Filter by status")

    # show
    p_show = sub.add_parser("show", help="Display details of a specific contract")
    p_show.add_argument("contract_id", type=int, help="Contract ID")

    # import-contract
    p_imp = sub.add_parser("import-contract", help="Ingest a contract file and run AI clause analysis")
    p_imp.add_argument("file_path", type=str, help="Path to contract text document")
    p_imp.add_argument("--number", required=True, help="Unique contract number (e.g. CNT-2026-001)")
    p_imp.add_argument("--counterparty", required=True, help="Counterparty organization name")
    p_imp.add_argument("--type", default="MSA", choices=[t.value for t in ContractType], help="Contract type")
    p_imp.add_argument("--value", type=float, default=0.0, help="Total contract value")
    p_imp.add_argument("--expires", type=str, default=None, help="Expiration date (YYYY-MM-DD)")

    # scan-expiries
    p_scan = sub.add_parser("scan-expiries", help="Scan contracts for impending expiration deadlines")

    # stats
    p_stats = sub.add_parser("stats", help="Compute portfolio valuation and risk breakdown")

    # export-report
    p_exp = sub.add_parser("export-report", help="Export executive portfolio report")
    p_exp.add_argument("--format", choices=["json", "csv", "md"], default="md", help="Export format")

    return parser

def main(args=None):
    parser = build_parser()
    opts = parser.parse_args(args)
    conn = get_db()
    contract_repo = ContractRepository(conn)
    company_repo = CompanyRepository(conn)

    if opts.subcommand == "init-db":
        DatabaseEngine.get_instance().init_schema()
        print("✅ Database schema initialized successfully.")

    elif opts.subcommand == "list":
        st = ContractStatus(opts.status) if opts.status else None
        contracts = contract_repo.list_contracts(status=st)
        print(f"\n{'ID':<4} {'NUMBER':<16} {'STATUS':<14} {'VALUE ($)':<12} {'EXPIRY':<12} {'COUNTERPARTY':<25} {'TITLE'}")
        print("-" * 105)
        for c in contracts:
            print(f"{c.id:<4} {c.contract_number:<16} {c.status.value:<14} {c.total_value:<12,.2f} {c.expiration_date or 'N/A':<12} {c.counterparty_name[:24]:<25} {c.title}")
        print(f"Total: {len(contracts)} contracts.\n")

    elif opts.subcommand == "show":
        c = contract_repo.get_by_id(opts.contract_id)
        if not c:
            print(f"Error: Contract #{opts.contract_id} not found.")
            sys.exit(1)
        clauses = contract_repo.get_clauses(c.id)
        print(f"\n================ {c.title} ({c.contract_number}) ================")
        print(f"Counterparty: {c.counterparty_name} | Type: {c.contract_type.value} | Status: {c.status.value}")
        print(f"Total Value: ${c.total_value:,.2f} | Term: {c.effective_date} to {c.expiration_date}")
        print(f"Risk Tier: {c.risk_tier} (Score: {c.risk_score}/100)")
        print(f"\n--- Extracted Clauses ({len(clauses)}) ---")
        for cl in clauses:
            print(f"• [{cl.clause_type.value}] {cl.title} (Risk: {cl.risk_score}/100)")
            if cl.risk_explanation and cl.risk_score >= 40:
                print(f"  Alert: {cl.risk_explanation}")
        print("==============================================================\n")

    elif opts.subcommand == "import-contract":
        p_path = Path(opts.file_path)
        if not p_path.exists():
            print(f"File not found: {opts.file_path}")
            sys.exit(1)
        with open(p_path, "rb") as f:
            raw_bytes = f.read()

        storage = DocumentStorage()
        rel_path, digest = storage.store_document(opts.number, p_path.name, raw_bytes)

        parser = DocumentParser()
        doc = parser.parse_text(raw_bytes.decode("utf-8", errors="ignore"), fallback_title=p_path.stem)

        c = Contract(
            title=doc.title,
            contract_number=opts.number,
            counterparty_name=opts.counterparty,
            contract_type=ContractType(opts.type),
            status=ContractStatus.DRAFT,
            total_value=opts.value,
            annual_value=opts.value,
            expiration_date=opts.expires,
            document_hash=digest,
            file_path=rel_path
        )
        saved = contract_repo.create(c)

        extractor = ClauseExtractor()
        extracted = extractor.extract_from_sections(doc.sections)
        for ec in extracted:
            cl = Clause(
                contract_id=saved.id,
                clause_type=ec.clause_type,
                title=ec.title,
                text=ec.text,
                is_standard=ec.is_standard,
                risk_score=ec.risk_score,
                risk_explanation=ec.risk_explanation,
                suggested_revision=ec.suggested_revision
            )
            contract_repo.add_clause(cl)

        clauses = contract_repo.get_clauses(saved.id)
        analyzer = RiskAnalyzer()
        assessment = analyzer.evaluate_risk(saved.id, clauses)
        saved.risk_score = assessment.overall_score
        saved.risk_tier = assessment.risk_tier.value
        saved.summary = ContractSummarizer.generate_executive_summary(saved, clauses, assessment)
        contract_repo.update(saved)

        print(f"✅ Ingested '{saved.title}' [ID: {saved.id}]")
        print(f"   Clauses: {len(clauses)} | Risk: {saved.risk_score}/100 ({saved.risk_tier})")

    elif opts.subcommand == "scan-expiries":
        contracts = contract_repo.list_contracts()
        alerts = ExpiryEngine().scan_all(contracts)
        print(f"\n{'URGENCY':<10} {'DAYS':<6} {'EXPIRATION':<12} {'CONTRACT':<16} {'COUNTERPARTY'}")
        print("-" * 75)
        for a in alerts:
            print(f"{a.urgency:<10} {a.days_remaining:<6} {a.expiration_date:<12} {a.contract_number:<16} {a.counterparty_name}")
        print(f"\nFound {len(alerts)} contracts requiring expiry review.\n")

    elif opts.subcommand == "stats":
        contracts = contract_repo.list_contracts()
        summary = PortfolioAnalytics.compute_summary(contracts)
        print("\n=== Contract Portfolio Analytics ===")
        print(f"Total Agreements: {summary.total_contracts} ({summary.active_contracts} Active)")
        print(f"Total Portfolio Value: ${summary.total_contract_value:,.2f}")
        print(f"Annual Recurring Spend: ${summary.annual_recurring_spend:,.2f}")
        print(f"Average Contract Value: ${summary.avg_contract_value:,.2f}")
        print("\nRisk Distribution:", dict(summary.risk_tier_distribution))
        print("Status Distribution:", dict(summary.status_distribution))
        print("====================================\n")

    elif opts.subcommand == "export-report":
        contracts = contract_repo.list_contracts()
        summary = PortfolioAnalytics.compute_summary(contracts)
        if opts.format == "csv":
            print(ReportExporter.export_csv(contracts))
        elif opts.format == "json":
            print(ReportExporter.export_json(contracts, summary))
        else:
            print(ReportExporter.export_markdown_report(contracts, summary))

if __name__ == "__main__":
    main()
