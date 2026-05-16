# WealthPilot — AI Co-Pilot for Independent Financial Advisors
![Uploading Screenshot 2026-05-16 at 8.19.38 AM.png…]()

**Columbia IEORE4576 Capstone Project — Spring 2026**
**Student:** Kanchan Bhale (kvb2117)

## Live URL
https://wealthpilot-1026658918129.us-central1.run.app

## What It Does
WealthPilot is a multi-agent AI system giving independent RIAs a smart morning brief — surfacing which client accounts need attention, why, and what to do about it.

Every morning the advisor opens WealthPilot and it has already:
- Checked all accounts for allocation drift (Agent 1)
- Run suitability checks against each client's IPS (Agent 2)
- Found tax loss harvesting opportunities and estimated savings (Agent 1)
- Drafted personalized client emails via Gemini (Agent 3)

## Run Locally
```bash

## Class Concepts Used (IEORE4576)

| Concept | Where Used | File |
|---------|-----------|------|
| Multi-Agent Orchestration | 3 specialized agents coordinated by orchestrator | orchestrator.py, agents/ |
| Structured Output | Every agent returns typed validated dicts; compliance memo has rigid schema | tools/suitability_tools.py |
| LLM Tool Use / Prompting | Communication agent uses Gemini with per-client context injection | agents/communication_agent.py |
| Parallel Execution | Portfolio monitor processes all accounts in one pass | agents/portfolio_monitor.py |
| RAG | Client IPS docs retrieved per-client and injected into LLM prompt | agents/communication_agent.py |
| Human-in-the-Loop | Advisor approves all orders and emails before execution | app.py |

## Project Structure
## Business Case
- **User:** Independent RIA, 50-150 clients, $50M-$500M AUM
- **Problem:** 12-15 hrs/month on manual drift checks, TLH, client emails
- **Price:** $299/month per advisor
- **COGS:** ~$13/month (tokens + Cloud Run)
- **Gross Margin:** ~96%
- **TAM:** 15,000 US independent RIAs

See BUSINESS_ONEPAGER.md for full business document.
