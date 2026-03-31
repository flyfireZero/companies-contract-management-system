# Companies Contract Management System (CCMS)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
[![Tests: Pytest](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

An enterprise-grade, AI-powered Contract Lifecycle Management (CLM) system designed to automate contract ingestion, clause analysis, multi-stage approval workflows, expiration forecasting, and risk intelligence.

---

## 🌟 Key Features

### 1. 🤖 AI Document Analysis & Clause Extraction
- **Multi-format Ingestion**: Ingests legal documents (PDF, DOCX, TXT) and parses them into hierarchical clause sections.
- **Intelligent Classification**: Detects critical legal clauses including *Confidentiality*, *Limitation of Liability*, *Indemnification*, *Governing Law*, *Termination*, *Payment Terms*, *Data Privacy/GDPR*, and *Audit Rights*.
- **Obligation Mining**: Automatically extracts deliverable milestones, compliance audit dates, and recurring payment terms.
- **Redline Recommendations**: Flags non-standard, unilateral, or unlimited liability clauses with turnkey recommended counter-language.

### 2. 🛡️ Enterprise Risk Intelligence
- **Composite Risk Scoring (0–100)**: Evaluates missing mandatory protections, uncapped damages, and one-sided indemnity.
- **Automated Escalation**: Identifies agreements requiring mandatory General Counsel approval.
- **Executive Summarizer**: Synthesizes multi-page contracts into a concise legal briefing and risk breakdown.

### 3. 🔄 Complete Lifecycle Governance
- **Deterministic State Machine**: Enforces enterprise transitions:
  `DRAFT` ➔ `IN_REVIEW` ➔ `APPROVED` ➔ `PENDING_SIGNATURE` ➔ `ACTIVE` ➔ `EXPIRING_SOON` ➔ `EXPIRED` / `RENEWED` / `TERMINATED`.
- **Validation Guards**: Prevents premature activation without validated execution dates or approval records.

### 4. ⏰ Automated Expiry & Milestone Radar
- **Multi-Window Alerts**: 90-day, 60-day, 30-day, and 7-day alert thresholds.
- **Auto-Renewal Traps**: Flags contracts approaching non-renewal notice cut-off deadlines.
- **Notification Dispatchers**: Formats webhook and email alert payloads.

### 5. 📊 Portfolio Analytics & Executive Dashboards
- Aggregates **Total Contract Value (TCV)**, **Annual Recurring Revenue/Spend (ARR)**, counterparty risk exposure, and stage cycle times.
- Interactive, responsive web dashboard with risk heatmaps and real-time expiration radars.
- Exports to CSV, JSON, and executive Markdown formats.

### 6. 🔒 Tamper-Evident Audit Logging & Diff Engine
- Immutable SHA-256 chain of custody for all contract modifications, transitions, and reviews.
- Contract amendment versioning with line-level unified text diff visualizer.

---

## 🏗️ Architecture

```
contract_management/
├── config.py                  # Global settings, paths, risk thresholds
├── models/                    # Data domain entities (Contract, Clause, Company, Risk, Audit)
├── db/                        # SQLite storage engine, connection manager, repositories
│   └── repositories/          # Contract, Company, and Audit data access layers
├── lifecycle/                 # State machine & 30/60/90-day expiry engine
├── ingestion/                 # Document parser & SHA-256 checksum blob storage
├── ai/                        # Clause extractor, risk analyzer, obligation miner, summarizer
├── analytics/                 # TCV/ARR aggregator, renewal forecasting, CSV/JSON exporter
├── audit/                     # Tamper-evident hash chain logging & clause diff engine
├── notifications/             # Multi-channel expiry and milestone alerts
├── api/                       # REST application router & JSON endpoints
├── cli/                       # `contractctl` command-line tool
└── ui/                        # Built-in modern web dashboard & templates
```

---

## 🚀 Quickstart

### 1. Installation
Clone the repository and inspect the environment:
```bash
git clone https://github.com/flyfireZero/companies-contract-management-system.git
cd companies-contract-management-system
```

Install optional dependencies or run out-of-the-box using the Python standard library:
```bash
pip install -e ".[dev]"
```

### 2. Seed Sample Data
Initialize the database and populate sample enterprise agreements:
```bash
python3 data/seed.py
```

### 3. Using the CLI (`contractctl`)
The `contractctl` CLI provides comprehensive terminal operations:

```bash
# List all active contracts
./contractctl list

# Inspect a contract with AI clause breakdown
./contractctl show 1

# Scan for expiring agreements across the portfolio
./contractctl scan-expiries

# Compute portfolio valuation and risk breakdown
./contractctl stats

# Export portfolio executive report to CSV or Markdown
./contractctl export-report --format md
```

### 4. Launching the Web Dashboard
Start the local dashboard server:
```bash
python3 -m contract_management.ui.server --port 8080
```
Open **http://localhost:8080** in your browser to view metrics, risk distributions, and the expiration radar.

---

## 🧪 Testing

Run the comprehensive pytest suite:
```bash
pytest tests/ -v
```

All unit, integration, and end-to-end tests validate:
- SQLite repository persistence & query filtering
- State machine transition rules & guards
- Expiry radar calculations (30/60/90 days)
- Heuristic AI clause extraction & obligation mining
- Risk scoring algorithms & red-flag detection
- Portfolio analytics & reporting
- Tamper-evident audit hash integrity

---

## 📜 License
Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.
