import http.server
import socketserver
import json
from pathlib import Path
from contract_management.db.connection import get_db
from contract_management.db.repositories.contract_repo import ContractRepository
from contract_management.lifecycle.expiry_engine import ExpiryEngine
from contract_management.analytics.stats import PortfolioAnalytics
from contract_management.models.contract import ContractStatus

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path.startswith("/dashboard"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = self.render_dashboard()
            self.wfile.write(html.encode("utf-8"))
        elif self.path == "/api/stats":
            conn = get_db()
            contracts = ContractRepository(conn).list_contracts()
            summary = PortfolioAnalytics.compute_summary(contracts)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(summary.__dict__, default=str).encode("utf-8"))
        else:
            self.send_error(404, "Page not found")

    def render_dashboard(self) -> str:
        template_path = Path(__file__).parent / "templates" / "index.html"
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()

        conn = get_db()
        repo = ContractRepository(conn)
        contracts = repo.list_contracts()
        summary = PortfolioAnalytics.compute_summary(contracts)
        alerts = ExpiryEngine().scan_all(contracts)

        # Build contract rows
        rows = []
        for c in contracts:
            risk_color = (
                "bg-red-500/20 text-red-400 border-red-500/30" if c.risk_tier == "CRITICAL"
                else "bg-amber-500/20 text-amber-400 border-amber-500/30" if c.risk_tier == "HIGH"
                else "bg-blue-500/20 text-blue-400 border-blue-500/30" if c.risk_tier == "MEDIUM"
                else "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
            )
            status_color = (
                "bg-emerald-500/20 text-emerald-400" if c.status == ContractStatus.ACTIVE
                else "bg-amber-500/20 text-amber-400" if c.status == ContractStatus.EXPIRING_SOON
                else "bg-slate-700/50 text-slate-300"
            )
            rows.append(f"""
            <tr class="hover:bg-slate-800/40 transition-colors">
                <td class="px-6 py-4">
                    <div class="font-medium text-white">{c.title}</div>
                    <div class="text-xs text-slate-400">{c.contract_number} • {c.counterparty_name}</div>
                </td>
                <td class="px-4 py-4 text-xs font-mono text-slate-300">{c.contract_type.value}</td>
                <td class="px-4 py-4"><span class="px-2 py-0.5 rounded text-xs font-medium {status_color}">{c.status.value}</span></td>
                <td class="px-4 py-4 font-mono">${c.total_value:,.2f}</td>
                <td class="px-4 py-4"><span class="px-2 py-0.5 rounded border text-xs font-medium {risk_color}">{c.risk_tier}</span></td>
                <td class="px-6 py-4 text-xs text-slate-400">{c.expiration_date or 'N/A'}</td>
            </tr>
            """)

        # Build alert items
        alert_html = []
        for a in alerts[:5]:
            badge = "bg-red-500/20 text-red-400" if a.urgency in ["CRITICAL", "EXPIRED"] else "bg-amber-500/20 text-amber-400"
            alert_html.append(f"""
            <div class="p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-xs flex justify-between items-center">
                <div>
                    <div class="font-medium text-white">{a.contract_number}</div>
                    <div class="text-slate-400">{a.counterparty_name} • Exp: {a.expiration_date}</div>
                </div>
                <span class="px-2 py-1 rounded font-semibold {badge}">{a.days_remaining}d</span>
            </div>
            """)
        if not alert_html:
            alert_html.append('<div class="text-xs text-slate-400 italic">No urgent contract expirations.</div>')

        # Build risk breakdown
        risk_html = []
        for tier in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            count = summary.risk_tier_distribution.get(tier, 0)
            pct = round((count / max(1, summary.total_contracts)) * 100)
            bar_color = "bg-emerald-500" if tier == "LOW" else "bg-blue-500" if tier == "MEDIUM" else "bg-amber-500" if tier == "HIGH" else "bg-red-500"
            risk_html.append(f"""
            <div class="text-xs">
                <div class="flex justify-between text-slate-300 mb-1">
                    <span>{tier}</span>
                    <span>{count} ({pct}%)</span>
                </div>
                <div class="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                    <div class="{bar_color} h-full" style="width: {pct}%"></div>
                </div>
            </div>
            """)

        filled = template.replace("${total_value}", f"{summary.total_contract_value:,.2f}")
        filled = filled.replace("${annual_spend}", f"{summary.annual_recurring_spend:,.2f}")
        filled = filled.replace("${total_contracts}", str(summary.total_contracts))
        filled = filled.replace("${active_contracts}", str(summary.active_contracts))
        filled = filled.replace("${alerts_count}", str(len(alerts)))
        filled = filled.replace("${contract_rows}", "\n".join(rows))
        filled = filled.replace("${alert_items}", "\n".join(alert_html))
        filled = filled.replace("${risk_breakdown}", "\n".join(risk_html))
        return filled

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def run_server(host: str = "0.0.0.0", port: int = 8080):
    server = ReusableTCPServer((host, port), DashboardHandler)
    display_host = "localhost" if host == "0.0.0.0" else host
    print(f"🚀 LexiContract AI Dashboard serving at http://{display_host}:{port} (bound to {host}:{port})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        print("\nServer closed.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="LexiContract AI Web Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host interface to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on (default: 8080)")
    args = parser.parse_args()
    run_server(host=args.host, port=args.port)
