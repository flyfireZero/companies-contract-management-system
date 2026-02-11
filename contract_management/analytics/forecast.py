from typing import List, Dict, Any
from datetime import datetime
from contract_management.models.contract import Contract

class RenewalForecastEngine:
    """
    Forecasts upcoming contract renewals, expiration volumes, and capital requirements by month.
    """

    @classmethod
    def generate_monthly_forecast(cls, contracts: List[Contract]) -> Dict[str, Any]:
        monthly_expiries: Dict[str, int] = {}
        monthly_value_at_risk: Dict[str, float] = {}
        auto_renew_count = 0

        for c in contracts:
            if c.auto_renew:
                auto_renew_count += 1
            if not c.expiration_date:
                continue

            month_key = c.expiration_date[:7]  # YYYY-MM
            monthly_expiries[month_key] = monthly_expiries.get(month_key, 0) + 1
            monthly_value_at_risk[month_key] = monthly_value_at_risk.get(month_key, 0.0) + c.total_value

        sorted_months = sorted(monthly_expiries.keys())
        timeline = []
        for m in sorted_months:
            timeline.append({
                "month": m,
                "expiring_count": monthly_expiries[m],
                "value_at_risk": round(monthly_value_at_risk[m], 2)
            })

        return {
            "forecast_timeline": timeline,
            "total_tracked_expirations": sum(monthly_expiries.values()),
            "total_auto_renew_agreements": auto_renew_count
        }
