
import streamlit as st
import json, pandas as pd, plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="WealthPilot",page_icon="⚡",layout="wide",initial_sidebar_state="expanded")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background-color:#0a0e1a;color:#e2e8f0;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0d1117 0%,#0a0e1a 100%);border-right:1px solid #1e2432;}
[data-testid="stSidebar"] *{color:#c9d1d9 !important;}
.metric-card{background:linear-gradient(135deg,#111827,#1a2236);border:1px solid #1e2d4a;border-radius:12px;padding:20px;text-align:center;}
.metric-value{font-size:2rem;font-weight:700;color:#00d4aa;}
.metric-label{font-size:0.75rem;color:#8892a4;text-transform:uppercase;letter-spacing:0.08em;margin-top:4px;}
.section-header{color:#00d4aa;font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:12px;padding-bottom:6px;border-bottom:1px solid #1e2d4a;}
.stTabs [data-baseweb="tab-list"]{background-color:#111827;border-radius:8px;}
.stTabs [data-baseweb="tab"]{color:#8892a4;}
.stTabs [aria-selected="true"]{color:#00d4aa !important;}
.stButton>button{background:linear-gradient(135deg,#00d4aa,#0099ff);color:#0a0e1a;font-weight:700;border:none;border-radius:8px;padding:10px 24px;}
.email-box{background:#0d1117;border:1px solid #1e2d4a;border-radius:10px;padding:20px;font-family:monospace;font-size:0.85rem;color:#c9d1d9;white-space:pre-wrap;}
</style>""",unsafe_allow_html=True)

st.markdown("""<div style="background:linear-gradient(90deg,#0d1117,#111827);border-bottom:1px solid #1e2d4a;padding:16px 24px;display:flex;align-items:center;justify-content:space-between;margin-bottom:24px;">
<div><div style="font-size:1.8rem;font-weight:800;background:linear-gradient(135deg,#00d4aa,#0099ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">⚡ WealthPilot</div>
<div style="color:#8892a4;font-size:0.8rem;letter-spacing:0.15em;text-transform:uppercase;">AI Co-Pilot for Independent Financial Advisors</div></div>
<div style="color:#00d4aa;font-size:0.8rem;">● LIVE</div></div>""",unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ⚡ WealthPilot")
    st.markdown("---")
    st.markdown("**MORNING BRIEF**")
    run_brief = st.button("🚀  RUN MORNING BRIEF",use_container_width=True)
    st.markdown("---")
    st.markdown("**SETTINGS**")
    gen_emails = st.checkbox("Generate Emails (Gemini)",value=True)
    drift_thr  = st.slider("Drift Threshold (%)",2,10,5)
    tlh_min    = st.slider("Min TLH Loss ($)",500,5000,1000,step=500)
    st.markdown("---")
    st.markdown("**ADVISOR**")
    st.markdown("Jane Smith, CFA")
    st.markdown("*Smith Capital Management*")
    st.markdown("📋 6 clients | $9.3M AUM")
    st.markdown("---")
    st.markdown("<div style=\'font-size:0.7rem;color:#4a5568;\'>Columbia IEORE4576<br>Capstone — Spring 2026</div>",unsafe_allow_html=True)

if "brief" not in st.session_state: st.session_state.brief=None
if "sel" not in st.session_state: st.session_state.sel=None

if run_brief:
    import config as _cfg
    _cfg.DRIFT_THRESHOLD=drift_thr; _cfg.TLH_MIN_LOSS=tlh_min
    msgs=[]
    prog=st.empty()
    def cb(m):
        msgs.append(m); prog.markdown(chr(10).join(f"⚡ {x}" for x in msgs[-3:]))
    from orchestrator import run_morning_brief,load_data
    c,p=load_data()
    with st.spinner("Running pipeline..."):
        st.session_state.brief=run_morning_brief(clients=c,portfolios=p,generate_emails=gen_emails,status_callback=cb)
    prog.empty(); st.success("Morning brief complete!")

if st.session_state.brief:
    brief=st.session_state.brief; summary=brief["summary"]; results=brief["client_results"]
    st.markdown('<div class="section-header">MORNING BRIEF SUMMARY</div>',unsafe_allow_html=True)
    cols=st.columns(6)
    for col,(lbl,val) in zip(cols,[("Total AUM",f"${summary['total_aum']/1e6:.1f}M"),("Clients",str(summary["total_clients"])),("Need Action",str(summary["accounts_need_action"])),("Rebalance",str(summary["needs_rebalance"])),("TLH Opps",str(summary["tlh_opportunities"])),("Tax Savings",f"${summary['estimated_tlh_savings']:,.0f}")]):
        col.markdown(f'''<div class="metric-card"><div class="metric-value">{val}</div><div class="metric-label">{lbl}</div></div>''',unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    left,right=st.columns([1,2],gap="large")
    with left:
        st.markdown('<div class="section-header">CLIENT ACTION QUEUE</div>',unsafe_allow_html=True)
        for r in results:
            c2=r["client"]; al=r["alert_level"]
            color={"RED":"#ff6b6b","YELLOW":"#ffd93d","GREEN":"#00d4aa"}[al]
            icon={"RED":"⚠","YELLOW":"⚡","GREEN":"✓"}[al]
            label=f"{icon} {c2['name']} | ${r['portfolio_state']['total_value']/1e6:.2f}M | Drift {r['portfolio_state']['max_drift']:.1f}% | TLH:{len(r['tlh_candidates'])}"
            if st.button(label,key=f"c_{c2['id']}",use_container_width=True):
                st.session_state.sel=c2["id"]
    with right:
        if st.session_state.sel:
            cid=st.session_state.sel
            result=next((r for r in results if r["client"]["id"]==cid),None)
            if result:
                cl=result["client"]; state=result["portfolio_state"]; suit=result["suitability"]
                orders=result["rebalance_orders"]; tlh=result["tlh_candidates"]; memo=result["compliance_memo"]; email=result.get("draft_email")
                st.markdown(f'''<div class="section-header">{cl["name"].upper()} — DEEP DIVE</div>''',unsafe_allow_html=True)
                ic=st.columns(4)
                ic[0].metric("Age",cl["age"]); ic[1].metric("Risk",cl["risk_tolerance"].title())
                ic[2].metric("AUM",f"${state['total_value']/1e6:.2f}M"); ic[3].metric("Alert",result["alert_level"])
                tabs=st.tabs(["📊 Portfolio","⚖️ Suitability","💸 Rebalance","🌿 TLH","📧 Email","📋 Memo"])
                with tabs[0]:
                    df=pd.DataFrame(state["drift_analysis"])
                    fig=go.Figure()
                    fig.add_trace(go.Bar(name="Target %",x=df["asset_class"],y=df["target_pct"],marker_color="#0099ff",opacity=0.6))
                    fig.add_trace(go.Bar(name="Current %",x=df["asset_class"],y=df["current_pct"],marker_color="#00d4aa"))
                    fig.update_layout(barmode="group",paper_bgcolor="#0a0e1a",plot_bgcolor="#111827",font_color="#e2e8f0",margin=dict(l=0,r=0,t=10,b=0),height=240)
                    st.plotly_chart(fig,use_container_width=True)
                    hdf=pd.DataFrame(state["holding_details"])[["ticker","name","asset_class","current_value","unrealized_pnl","unrealized_pct"]]
                    hdf.columns=["Ticker","Name","Class","Value ($)","P&L ($)","P&L %"]
                    hdf["Value ($)"]=hdf["Value ($)"].apply(lambda x:f"${x:,.0f}")
                    hdf["P&L ($)"]=hdf["P&L ($)"].apply(lambda x:f"${x:,.0f}")
                    hdf["P&L %"]=hdf["P&L %"].apply(lambda x:f"{x:+.1f}%")
                    st.dataframe(hdf,use_container_width=True,hide_index=True)
                with tabs[1]:
                    sc={"OK":"#00d4aa","MEDIUM":"#ffd93d","HIGH":"#ff6b6b"}[suit["suitability_status"]]
                    st.markdown(f'''<div style="background:#111827;border:1px solid {sc}44;border-radius:10px;padding:16px;margin-bottom:12px;"><div style="color:{sc};font-weight:700;font-size:1.1rem;">Status: {suit["suitability_status"]}</div><div style="color:#8892a4;font-size:0.85rem;margin-top:6px;">{suit["ips_notes"]}</div></div>''',unsafe_allow_html=True)
                    if suit["flags"]:
                        for f in suit["flags"]:
                            fc={"HIGH":"#ff6b6b","MEDIUM":"#ffd93d","LOW":"#00d4aa"}[f["severity"]]
                            st.markdown(f'''<div style="background:#0d1117;border-left:3px solid {fc};padding:10px 14px;border-radius:0 6px 6px 0;margin-bottom:8px;"><span style="color:{fc};font-weight:700;">[{f["severity"]}]</span> <span style="color:#c9d1d9;">{f["flag"]}</span><br><span style="color:#8892a4;font-size:0.85rem;">{f["detail"]}</span></div>''',unsafe_allow_html=True)
                    else: st.success("No suitability flags.")
                with tabs[2]:
                    if orders:
                        for o in orders:
                            ac="#00d4aa" if o["action"]=="BUY" else "#ff6b6b"
                            st.markdown(f'''<div style="background:#111827;border:1px solid #1e2d4a;border-radius:8px;padding:14px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;"><div><span style="color:{ac};font-weight:700;">{o["action"]}</span> <span style="color:#e2e8f0;">{o["asset_class"].replace("_"," ").title()}</span><div style="color:#8892a4;font-size:0.8rem;">{o["reason"]}</div></div><div style="color:{ac};font-weight:700;">${o["amount_usd"]:,.0f}</div></div>''',unsafe_allow_html=True)
                        if st.button("✅ Approve Orders",key=f"app_{cid}"): st.success("Orders approved! Memo generated.")
                    else: st.success(f"Portfolio within {drift_thr}% drift threshold.")
                with tabs[3]:
                    if tlh:
                        tot=sum(abs(t["unrealized_loss"]) for t in tlh)
                        st.metric("Harvestable Losses",f"${tot:,.0f}"); st.metric("Est. Tax Savings (37%)",f"${tot*0.37:,.0f}")
                        for t in tlh:
                            st.markdown(f'''<div style="background:#111827;border:1px solid #1e2d4a;border-radius:8px;padding:14px;margin-bottom:8px;display:flex;justify-content:space-between;"><div><span style="color:#e2e8f0;font-weight:700;">{t["ticker"]}</span> <span style="color:#8892a4;">{t["name"]}</span><div style="color:#8892a4;font-size:0.8rem;margin-top:4px;">{t["harvest_action"]}</div></div><span style="color:#ff6b6b;font-weight:700;">${abs(t["unrealized_loss"]):,.0f} ({t["loss_pct"]:.1f}%)</span></div>''',unsafe_allow_html=True)
                        st.warning("Wash sale rule: 30-day window applies.")
                    else: st.info("No TLH opportunities above threshold.")
                with tabs[4]:
                    if email:
                        st.markdown("**AI-Drafted Email** (review before sending)")
                        st.markdown(f'''<div class="email-box">{email}</div>''',unsafe_allow_html=True)
                        c3,c4=st.columns(2)
                        if c3.button("📤 Approve & Send",key=f"send_{cid}"): st.success(f"Email queued for {cl['email']}")
                    else: st.info("No email generated (disabled or not needed).")
                with tabs[5]:
                    st.text(memo)
                    if st.button("💾 Save to Record",key=f"save_{cid}"): st.success("Saved.")
        else:
            st.markdown('''<div style="text-align:center;padding:80px 20px;color:#4a5568;"><div style="font-size:3rem;">⚡</div><div style="font-size:1.1rem;margin-top:12px;">Select a client from the queue</div><div style="font-size:0.85rem;margin-top:8px;">Run Morning Brief first, then click any client.</div></div>''',unsafe_allow_html=True)
else:
    st.markdown('''<div style="text-align:center;padding:80px 40px;"><div style="font-size:4rem;">⚡</div><h1 style="background:linear-gradient(135deg,#00d4aa,#0099ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:2.5rem;font-weight:800;">WealthPilot</h1><p style="color:#8892a4;font-size:1.1rem;max-width:600px;margin:16px auto;">AI-powered morning brief for independent financial advisors.<br>Drift detection · Tax loss harvesting · Suitability compliance · Client communications.</p><div style="margin-top:40px;display:flex;justify-content:center;gap:32px;flex-wrap:wrap;"><div style="background:#111827;border:1px solid #1e2d4a;border-radius:12px;padding:20px 28px;"><div style="color:#00d4aa;font-size:1.5rem;font-weight:700;">3</div><div style="color:#8892a4;font-size:0.8rem;">AI AGENTS</div></div><div style="background:#111827;border:1px solid #1e2d4a;border-radius:12px;padding:20px 28px;"><div style="color:#00d4aa;font-size:1.5rem;font-weight:700;">6</div><div style="color:#8892a4;font-size:0.8rem;">CLASS CONCEPTS</div></div><div style="background:#111827;border:1px solid #1e2d4a;border-radius:12px;padding:20px 28px;"><div style="color:#00d4aa;font-size:1.5rem;font-weight:700;">$299/mo</div><div style="color:#8892a4;font-size:0.8rem;">PER ADVISOR</div></div><div style="background:#111827;border:1px solid #1e2d4a;border-radius:12px;padding:20px 28px;"><div style="color:#00d4aa;font-size:1.5rem;font-weight:700;">96%</div><div style="color:#8892a4;font-size:0.8rem;">GROSS MARGIN</div></div></div><p style="color:#4a5568;font-size:0.85rem;margin-top:48px;">Click <strong style="color:#00d4aa;">🚀 RUN MORNING BRIEF</strong> in the sidebar to start.</p></div>''',unsafe_allow_html=True)
