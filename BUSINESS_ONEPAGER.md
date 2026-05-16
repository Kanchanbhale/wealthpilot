# WealthPilot Business One-Pager

**Columbia IEORE4576 | Capstone | Spring 2026 | Kanchan Bhale (kvb2117)**

## The User
Independent Registered Investment Advisors (RIAs) managing $50M-$500M AUM. Solo practitioners or small teams (1-5 people) who left wirehouses to run their own book. They have 60-120 clients, no quant team, no Bloomberg terminal — just Excel, their custodian portal, and their CRM.

**Concrete persona:** Jane Smith, CFA. 20 years at Merrill Lynch, went independent 4 years ago. Manages 82 clients, $180M AUM. Spends Sunday evenings manually reviewing drift reports.

## The Problem
Jane's Monday morning: export 82 CSVs from Schwab, paste into Excel, manually check drift vs targets, check IPS compliance for each proposed trade, draft client emails from scratch. This takes 12-15 hours per month before she touches client work. She misses an average of $8,400/year in TLH savings per client due to infrequent review.

The tools that solve this exist for $250,000/year (Bloomberg, Orion, Black Diamond). WealthPilot delivers institutional-grade morning intelligence at $299/month.

## The Economics

**Pricing:** $299/month per advisor ($2,990/year)

| Item | Cost |
|------|------|
| Gemini 2.0 Flash tokens (80 clients x 30 days) | $3.20 |
| GCP Cloud Run | $6.00 |
| Storage, logging, monitoring | $1.50 |
| Support allocation | $2.30 |
| **Total COGS** | **$13.00** |
| **Revenue** | **$299.00** |
| **Gross Margin** | **95.7%** |

**TAM:** 15,000 independent RIAs in the US. 1% penetration = $540K ARR.

## Why These Technical Choices?

**Multi-Agent Architecture:** Portfolio math (deterministic), compliance checking (rule-based), and email drafting (creative) have fundamentally different data needs and risk tolerances. Separating them means each can be tested and audited independently — critical for a regulated financial product.

**Structured Output at Every Stage:** Regulators need machine-readable audit trails, not paragraphs. Every agent produces typed, validated dictionaries.

**RAG for Suitability:** Each client's IPS is firm-specific. We retrieve the relevant client's IPS at query time and inject it into context — retrieval-augmented generation applied to compliance.

**Gemini via Vertex AI:** Cheapest capable model with enterprise security and data residency guarantees financial services requires.

**Human-in-the-Loop:** No trade executes, no email sends, without advisor approval. Fiduciary duty requires it. This reduces regulatory risk and differentiates from robo-advisors.

## Go-To-Market
- Phase 1: NAPFA member outreach, 90-day free trial for first 20 advisors
- Phase 2: Custodian partnerships (Schwab, Fidelity RIA channel)
- Phase 3: API integration with Orion/Nitrogen as intelligence layer
