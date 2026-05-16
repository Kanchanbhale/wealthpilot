from __future__ import annotations
import os

def draft_client_email(client, analysis):
    try:
        import google.genai as genai
        state=analysis["portfolio_state"]; tlh=analysis["tlh_candidates"]; orders=analysis["rebalance_orders"]
        tone="calm reassuring simple 3 paragraphs" if client["risk_tolerance"]=="conservative" or client["age"]>=65 else ("direct analytical with numbers" if client["risk_tolerance"]=="aggressive" else "professional balanced 3-4 paragraphs")
        ctx=[f"Client: {client['name']}, age {client['age']}, {client['risk_tolerance']} risk, portfolio ${state['total_value']:,.0f}"]
        if orders: ctx.append("Rebalancing: "+" | ".join(f"{o['action']} {o['asset_class']} ${o['amount_usd']:,.0f}" for o in orders))
        if tlh: ctx.append("TLH: "+" | ".join(f"{t['ticker']} loss ${abs(t['unrealized_loss']):,.0f}" for t in tlh))
        prompt=f"You are a financial advisor. Tone: {tone}.\nContext: {chr(10).join(ctx)}\nWrite a client email with Subject line then body. Sign as Your Advisory Team. No return promises."
        gc=genai.Client(vertexai=True,project=os.getenv("GOOGLE_CLOUD_PROJECT","ieor-agentic-1"),location=os.getenv("GOOGLE_CLOUD_LOCATION","us-central1"))
        return gc.models.generate_content(model=os.getenv("GEMINI_MODEL","gemini-2.0-flash"),contents=prompt).text
    except Exception:
        return _fallback(client,analysis)

def _fallback(client,analysis):
    name=client["name"].split()[0]; orders=analysis["rebalance_orders"]; tlh=analysis["tlh_candidates"]
    lines=[f"Subject: Portfolio Update","",f"Dear {name},","",f"Your account is valued at ${analysis['portfolio_state']['total_value']:,.0f}."]
    if orders: lines+=["","Recommended rebalancing:"]+[f"  - {o['action']} {o['asset_class']}: ~${o['amount_usd']:,.0f}" for o in orders]
    if tlh: lines+=["","Tax loss harvesting opportunities:"]+[f"  - {t['ticker']}: ${abs(t['unrealized_loss']):,.0f} loss" for t in tlh]
    lines+=["","No trades without your approval.","","Your Advisory Team"]
    return chr(10).join(lines)

def draft_all_emails(results):
    out=[]
    for r in results:
        email=draft_client_email(r["client"],r) if (r["action_required"] or r["suitability"]["flags"]) else None
        out.append({**r,"draft_email":email})
    return out
