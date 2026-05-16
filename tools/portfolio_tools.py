from __future__ import annotations
import json
from config import DRIFT_THRESHOLD, TLH_MIN_LOSS, RISK_TOLERANCE_MAP

def compute_portfolio_state(client, portfolio):
    holdings = portfolio["holdings"]
    total_value = sum(h["shares"]*h["current_price"] for h in holdings)
    class_values = {}
    for h in holdings:
        cls = h["asset_class"]
        class_values[cls] = class_values.get(cls,0) + h["shares"]*h["current_price"]
    target = client["target_allocation"]
    drift_analysis = []
    max_drift = 0.0
    for cls, target_pct in target.items():
        current_val = class_values.get(cls,0)
        current_pct = (current_val/total_value*100) if total_value>0 else 0
        drift = current_pct - target_pct
        drift_analysis.append({"asset_class":cls,"target_pct":target_pct,"current_pct":round(current_pct,2),"drift_pct":round(drift,2),"current_value":round(current_val,2)})
        max_drift = max(max_drift, abs(drift))
    holding_details = []
    for h in holdings:
        cv = h["shares"]*h["current_price"]
        cost = h["shares"]*h["cost_basis"]
        unreal = cv - cost
        holding_details.append({"ticker":h["ticker"],"name":h["name"],"asset_class":h["asset_class"],"shares":h["shares"],"current_price":h["current_price"],"cost_basis":h["cost_basis"],"current_value":round(cv,2),"unrealized_pnl":round(unreal,2),"unrealized_pct":round((unreal/cost*100) if cost>0 else 0,2)})
    return {"client_id":client["id"],"client_name":client["name"],"total_value":round(total_value,2),"drift_analysis":drift_analysis,"max_drift":round(max_drift,2),"needs_rebalance":max_drift>DRIFT_THRESHOLD,"holding_details":holding_details}

def find_tlh_candidates(portfolio_state):
    candidates = []
    for h in portfolio_state["holding_details"]:
        if h["unrealized_pnl"] < -TLH_MIN_LOSS and h["ticker"] != "CASH":
            candidates.append({"ticker":h["ticker"],"name":h["name"],"asset_class":h["asset_class"],"unrealized_loss":h["unrealized_pnl"],"current_value":h["current_value"],"loss_pct":h["unrealized_pct"],"harvest_action":f"Sell {h['ticker']} and replace with similar ETF to avoid wash sale"})
    candidates.sort(key=lambda x: x["unrealized_loss"])
    return candidates

def generate_rebalance_orders(client, portfolio_state):
    total_value = portfolio_state["total_value"]
    target = client["target_allocation"]
    orders = []
    for d in portfolio_state["drift_analysis"]:
        if abs(d["drift_pct"]) > DRIFT_THRESHOLD:
            target_val = total_value * target[d["asset_class"]] / 100
            delta = target_val - d["current_value"]
            orders.append({"asset_class":d["asset_class"],"action":"BUY" if delta>0 else "SELL","amount_usd":round(abs(delta),2),"reason":f"{d['asset_class']} drifted {d['drift_pct']:+.1f}% from target"})
    return orders

def check_cash_drag(portfolio_state, client):
    target_cash = client["target_allocation"].get("cash",5)
    actual_cash = next((d["current_pct"] for d in portfolio_state["drift_analysis"] if d["asset_class"]=="cash"),0)
    excess = actual_cash - target_cash
    return {"target_cash_pct":target_cash,"actual_cash_pct":round(actual_cash,2),"excess_cash_pct":round(excess,2),"has_cash_drag":excess>2.0,"excess_cash_usd":round(portfolio_state["total_value"]*excess/100,2) if excess>0 else 0}
