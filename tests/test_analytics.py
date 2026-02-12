from contract_management.models.contract import Contract, ContractStatus, ContractType
from contract_management.analytics.stats import PortfolioAnalytics
from contract_management.analytics.forecast import RenewalForecastEngine
from contract_management.analytics.exporter import ReportExporter

def test_portfolio_summary_computation():
    contracts = [
        Contract(title="C1", contract_number="1", status=ContractStatus.ACTIVE, contract_type=ContractType.MSA, total_value=100000.0, annual_value=50000.0, counterparty_name="Acme", risk_tier="LOW"),
        Contract(title="C2", contract_number="2", status=ContractStatus.ACTIVE, contract_type=ContractType.SOW, total_value=50000.0, annual_value=50000.0, counterparty_name="Beta Corp", risk_tier="HIGH"),
        Contract(title="C3", contract_number="3", status=ContractStatus.DRAFT, contract_type=ContractType.NDA, total_value=0.0, annual_value=0.0, counterparty_name="Acme", risk_tier="LOW")
    ]
    summary = PortfolioAnalytics.compute_summary(contracts)
    assert summary.total_contracts == 3
    assert summary.active_contracts == 2
    assert summary.total_contract_value == 150000.0
    assert summary.top_counterparties_by_value[0]["counterparty"] == "Acme"
    assert summary.risk_tier_distribution["HIGH"] == 1

def test_renewal_forecast():
    contracts = [
        Contract(title="C1", contract_number="1", expiration_date="2026-04-15", total_value=10000.0),
        Contract(title="C2", contract_number="2", expiration_date="2026-04-30", total_value=15000.0),
        Contract(title="C3", contract_number="3", expiration_date="2026-05-10", total_value=25000.0),
    ]
    forecast = RenewalForecastEngine.generate_monthly_forecast(contracts)
    assert len(forecast["forecast_timeline"]) == 2
    april = next(f for f in forecast["forecast_timeline"] if f["month"] == "2026-04")
    assert april["expiring_count"] == 2
    assert april["value_at_risk"] == 25000.0

def test_csv_export():
    contracts = [Contract(title="Test", contract_number="CNT-01", counterparty_name="Vendor")]
    csv_str = ReportExporter.export_csv(contracts)
    assert "contract_number,title" in csv_str
    assert "CNT-01,Test" in csv_str
