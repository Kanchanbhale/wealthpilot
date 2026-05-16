from __future__ import annotations
from tools.suitability_tools import check_allocation_suitability, check_trade_suitability, generate_compliance_memo

def run_suitability_checks(monitor_results):
    enriched=[]
    for r in monitor_results:
        client=r["client"]; state=r["portfolio_state"]; orders=r["rebalance_orders"]; tlh=r["tlh_candidates"]
        suit=check_allocation_suitability(client,state)
        trade_checks=[check_trade_suitability(client,{"action":o["action"],"amount_usd":o["amount_usd"],"asset_class":o["asset_class"]}) for o in orders]
        memo=generate_compliance_memo(client,suit,orders,tlh)
        alert="GREEN"
        if suit["suitability_status"]=="HIGH": alert="RED"
        elif suit["suitability_status"]=="MEDIUM" or r["action_required"]: alert="YELLOW"
        enriched.append({**r,"suitability":suit,"trade_checks":trade_checks,"compliance_memo":memo,"alert_level":alert})
    return enriched
