from __future__ import annotations
import json,time,datetime
from pathlib import Path
from agents.portfolio_monitor import run_portfolio_monitor,get_morning_brief_summary
from agents.suitability_agent import run_suitability_checks
from agents.communication_agent import draft_all_emails

def load_data():
    base=Path(__file__).parent/"data"
    return json.loads((base/"clients.json").read_text()),json.loads((base/"portfolios.json").read_text())

def run_morning_brief(clients=None,portfolios=None,generate_emails=True,status_callback=None):
    def s(m):
        if status_callback: status_callback(m)
    if clients is None: clients,portfolios=load_data()
    t0=time.time()
    s(f"Monitoring {len(clients)} accounts...")
    monitor=run_portfolio_monitor(clients,portfolios)
    s(f"{sum(1 for r in monitor if r['action_required'])} accounts need attention.")
    s("Running suitability checks...")
    enriched=run_suitability_checks(monitor)
    if generate_emails:
        s("Drafting emails via Gemini...")
        final=draft_all_emails(enriched)
        s("Done.")
    else:
        final=[{**r,"draft_email":None} for r in enriched]
    summary=get_morning_brief_summary(monitor)
    summary["pipeline_elapsed_sec"]=round(time.time()-t0,1)
    return {"summary":summary,"client_results":final,"generated_at":datetime.datetime.now().isoformat()}
