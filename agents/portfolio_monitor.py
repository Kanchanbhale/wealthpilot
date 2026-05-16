from __future__ import annotations
from tools.portfolio_tools import compute_portfolio_state, find_tlh_candidates, generate_rebalance_orders, check_cash_drag

def run_portfolio_monitor(clients, portfolios):
    results=[]
    for client in clients:
        cid=client["id"]
        if cid not in portfolios: continue
        state=compute_portfolio_state(client,portfolios[cid])
        tlh=find_tlh_candidates(state)
        orders=generate_rebalance_orders(client,state) if state["needs_rebalance"] else []
        cd=check_cash_drag(state,client)
        pri=3*state["needs_rebalance"]+2*len(tlh)+cd["has_cash_drag"]
        results.append({"client":client,"portfolio_state":state,"tlh_candidates":tlh,"rebalance_orders":orders,"cash_drag":cd,"priority_score":pri,"action_required":state["needs_rebalance"] or bool(tlh) or cd["has_cash_drag"]})
    results.sort(key=lambda x:x["priority_score"],reverse=True)
    return results

def get_morning_brief_summary(results):
    aum=sum(r["portfolio_state"]["total_value"] for r in results)
    tlh_savings=sum(abs(t["unrealized_loss"])*0.37 for r in results for t in r["tlh_candidates"])
    return {"total_clients":len(results),"accounts_need_action":sum(1 for r in results if r["action_required"]),"needs_rebalance":sum(1 for r in results if r["portfolio_state"]["needs_rebalance"]),"tlh_opportunities":sum(1 for r in results if r["tlh_candidates"]),"cash_drag_alerts":sum(1 for r in results if r["cash_drag"]["has_cash_drag"]),"total_aum":round(aum,2),"estimated_tlh_savings":round(tlh_savings,2),"top_priority_client":results[0]["client"]["name"] if results else None}
