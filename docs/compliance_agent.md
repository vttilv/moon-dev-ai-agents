# Compliance Agent

Ensures trading activities follow regulations.

## What It Does
- Monitors for wash trading
- Checks position limits
- Tracks tax obligations
- Generates compliance reports

## Usage
```bash
python src/agents/compliance_agent.py
```

## Checks
- No market manipulation
- Proper record keeping
- Tax loss harvesting opportunities
- Regulatory thresholds

## Configuration
```python
COMPLIANCE_JURISDICTION = 'US'
COMPLIANCE_REPORT_FREQUENCY = 'weekly'
```

## Reports
- Trade history CSV
- P&L statements
- Tax estimates
- Risk exposure summaries

## Output
`src/data/compliance_agent/[date]/compliance_report.pdf`