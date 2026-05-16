from __future__ import annotations
from config import RISK_TOLERANCE_MAP
import datetime

def check_allocation_suitability(client, portfolio_state):
    risk = client["risk_tolerance"]
    limits = RISK_TOLERANCE_MAP.get(risk, RISK_TOLERANCE_MAP["moderate"])
    eq = next((d["current_pct"] for d in portfolio_state["drift_analysis"] if d["asset_class"]=="equities"),0)
    fi = next((d["current_pct"] for d in portfolio_state["drift_analysis"] if d["asset_class"]=="fixed_income"),0)
    flags=[]; severity="OK"
    if eq > limits["max_equities"]:
        flags.append({"flag":"EQUITY_OVERWEIGHT","detail":f"Equity {eq:.1f}% exceeds max {limits['max_equities']}% for {risk}","severity":"HIGH"}); severity="HIGH"
    if fi < limits["min_fixed_income"]:
        flags.append({"flag":"FIXED_INCOME_UNDERWEIGHT","detail":f"Fixed income {fi:.1f}% below min {limits['min_fixed_income']}% for {risk}","severity":"HIGH"}); severity="HIGH"
    if client["age"]>=70 and eq>40:
        flags.append({"flag":"AGE_EQUITY_MISMATCH","detail":f"Age {client['age']}: equity {eq:.1f}% may be too high","severity":"MEDIUM"})
        if severity=="OK": severity="MEDIUM"
    if client["investment_horizon"]=="short" and eq>35:
        flags.append({"flag":"HORIZON_MISMATCH","detail":f"Short horizon with {eq:.1f}% equities","severity":"MEDIUM"})
        if severity=="OK": severity="MEDIUM"
    return {"client_id":client["id"],"client_name":client["name"],"risk_tolerance":risk,"suitability_status":severity,"flags":flags,"is_suitable":severity=="OK","ips_notes":client["ips_notes"]}

def check_trade_suitability(client, trade):
    flags=[]
    if trade.get("asset_class")=="equities" and client["age"]>=70 and client["risk_tolerance"]=="conservative":
        flags.append({"flag":"AGE_SUITABILITY","detail":f"Equity trade for age {client['age']} conservative client","severity":"HIGH"})
    if trade.get("action")=="BUY" and trade.get("amount_usd",0)>150000:
        flags.append({"flag":"CONCENTRATION_RISK","detail":f"Large single trade ${trade['amount_usd']:,.0f}","severity":"MEDIUM"})
    return {"trade":trade,"is_suitable":all(f["severity"]!="HIGH" for f in flags),"flags":flags,"recommendation":"APPROVE" if all(f["severity"]!="HIGH" for f in flags) else "REVIEW REQUIRED"}

def generate_compliance_memo(client, suit, orders, tlh):
    lines=[f"COMPLIANCE MEMO — {client['name']} ({client['id']})",
           f"Date: {datetime.date.today()}",
           f"Profile: {client['risk_tolerance'].upper()} | Age: {client['age']} | Horizon: {client['investment_horizon']}",
           "","SUITABILITY: "+suit["suitability_status"]]
    for f in suit["flags"]: lines.append(f"  [{f['severity']}] {f['flag']}: {f['detail']}")
    if not suit["flags"]: lines.append("  No flags.")
    if orders:
        lines+=["","REBALANCE ORDERS:"]
        for o in orders: lines.append(f"  {o['action']} {o['asset_class']}: ${o['amount_usd']:,.0f} — {o['reason']}")
    if tlh:
        lines+=["","TAX LOSS HARVESTING:"]
        for t in tlh: lines.append(f"  {t['ticker']}: loss ${abs(t['unrealized_loss']):,.0f} ({t['loss_pct']:.1f}%)")
    lines+=["",f"IPS: {client['ips_notes']}","","Advisor signature required."]
    return chr(10).join(lines)
