# AquaMitra — Your Digital Partner for Smarter Fish Farming

**Community-Focused Digital Fishery Pond Management & Decision-Support System**  
*An Engineering Community Service Project (CSP) — Computer Science & Engineering*

---

## 1. Executive Summary

AquaMitra is an offline-resilient, production-ready aquaculture management and decision-support web platform designed for fish farmers, aquaculture entrepreneurs, and pond communities. Built with Python and Streamlit, it delivers enterprise record-keeping, multi-pond health tracking, deterministic biological growth modeling, physicochemical water quality monitoring, weather awareness, financial accounting, and responsible contextual AI intelligence.

### Academic & Community Mission
- **Community Focus:** Empowers rural and semi-intensive fish farmers with accessible digital tools in both English and Telugu (తెలుగు).
- **Decision Support:** Provides structured operational guidance, anomaly identification, and proactive checklists. It does **not** replace fisheries veterinarians or provide medical disease diagnoses.
- **Deterministic Rigor:** Biological growth, biomass, feed ration models, and financial ledgers execute in deterministic Python algorithms with zero hallucination.

---

## 2. Core Architecture & Technology Stack

```
                              AQUAMITRA ARCHITECTURE
                              
   [ Farmer / Field Operator ]            [ Mobile / Tablet / Desktop ]
                │                                       │
                ▼                                       ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                AquaMitra Enterprise UI (Streamlit)              │
    │  - 15 Functional Menus        - 9 Quick Action Modal Dialogs    │
    │  - Touch Target WCAG 2.5.5    - Responsive 2-Column Mobile Grid │
    │  - Bilingual Switcher (EN/TE) - Zero-Emoji Design Tokens        │
    └─────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                   Data Access & Calculation Engine              │
    │  - Deterministic Biomass Model      - Feed Ration Variance      │
    │  - Water Quality Threshold Matrix   - Average Daily Growth (ADG)│
    │  - Financial Net Difference Ledger  - Documentation Completeness│
    └─────────────────────────────────────────────────────────────────┘
                    │                                 │
                    ▼                                 ▼
    ┌───────────────────────────────┐ ┌───────────────────────────────┐
    │     Dual-Tier Persistence     │ │     AI Decision Support       │
    │ 1. Local Resilient Store      │ │ - AquaMitra Local Engine      │
    │ 2. Microsoft SQL Server       │ │ - Optional Google Gemini API  │
    └───────────────────────────────┘ └───────────────────────────────┘
```

- **Frontend:** Streamlit, Custom Responsive CSS (`components/styles.py`), Plotly Interactive Charts.
- **Backend & Logic:** Python 3.10+, Pandas, NumPy.
- **Database Architecture:** Dual-tier persistence supporting Microsoft SQL Server (`pyodbc`) and local validated storage.
- **AI Integration:** Hybrid AI Engine (`AquaMitra Local Intelligence Engine` with optional `Google Gemini API` cloud bridge).
- **Design System:** Deep Navy (`#0F2942`), Teal (`#0D9488`), Cool Slate (`#F8FAFC`), and subtle border treatments with strict zero-emoji styling.

---

## 3. Comprehensive 15-Module Navigation

| # | Module | Key Capabilities |
|---|--------|------------------|
| 1 | **Overview** | Command Center, 8 KPI cards, AI Farm Status Synthesis, Pond Health Snapshots, Daily Advisory. |
| 2 | **Ponds** | Pond Registry, dimensions, water source tags, status filters, 10-tab command center. |
| 3 | **Fish** | Stocked batches, species registry, sampling growth log, calculated biomass, harvest log. |
| 4 | **Water Quality** | Parameter matrix (pH, DO, Temp, Turbidity, Ammonia), manual readings, trend graphs, baseline bounds. |
| 5 | **Feeding** | Feed application tracking, biomass ration model variance, warehouse stock inventory, feed cost metrics. |
| 6 | **Health & Incidents** | Non-diagnostic observation logging, mortality incident registry, follow-up tracking. |
| 7 | **Environment** | Regional agro-meteorological observations (Krishna-Godavari Delta), 5-day forecast, dissolved oxygen correlation. |
| 8 | **Finance** | Operational expenses, purchases, labour wages, fish sales proceeds, Estimated Net Difference. |
| 9 | **Assets** | Mechanical machinery inventory, aerator/pump maintenance schedule, certification document vault. |
| 10 | **Analytics** | Interactive Plotly cross-parameter visual analytics with "Explain with AI" buttons on all charts. |
| 11 | **Alerts** | Rule-based decision-support alerts (`[HIGH]`, `[WARNING]`, `[INFO]`), actionable next steps. |
| 12 | **Records** | Unified chronological activity feed, central archive search, 3-tier documentation completeness audit. |
| 13 | **AI Intelligence** | Grounded conversational companion, categorized anomaly insights, actionable recommendations. |
| 14 | **Reports** | Automated Farm, Pond, Water, Fish, Feed, Incident, and Financial summaries with CSV downloads. |
| 15 | **Settings** | 16-field Farm Profile editor, language switcher, reference range editor, dual persistence mode toggle. |

---

## 4. Quick Actions Bar

Accessible at the top of the workspace across all views:
1. `Add Pond` — Register new fishery ponds with soil and inlet/outlet specifications.
2. `Log Water` — Record pH, DO, Temperature, Turbidity, and Ammonia observations.
3. `Add Growth` — Record sampling batch sample counts and average fish weights.
4. `Log Feed` — Record daily feed disbursed with automatic ration variance analysis.
5. `Log Incident` — Log unexpected pond observations and remedial action taken.
6. `Add Expense` — Record feed, seed, electricity, chemical, or equipment expenditure.
7. `Record Sale` — Record wholesale or retail harvest revenue and buyer information.
8. `Record Harvest` — Record selective or final fish harvest hauls.
9. `Add Maintenance` — Schedule equipment servicing, aerator oiling, or net cleaning.

---

## 5. Deployment Guide

### Option A: Local Run
```bash
# 1. Clone repository
git clone https://github.com/Kodalimahesh-05/aquamitra.git
cd aquamitra

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch application
streamlit run app.py
```

### Option B: Streamlit Community Cloud (Recommended for Live Demo)
1. Fork or push this repository to GitHub under your account.
2. Visit [share.streamlit.io](https://share.streamlit.io).
3. Connect your GitHub account and select repository `aquamitra`.
4. Main file path: `app.py`.
5. Click **Deploy**. The platform automatically detects `requirements.txt` and `packages.txt`.

### Option C: Docker Container Deployment
```bash
docker build -t aquamitra .
docker run -p 8501:8501 aquamitra
```

---

## 6. Screenshots Gallery

High-resolution screenshots demonstrating full system execution are located in the `screenshots/` directory:

- `screenshots/01_overview_dashboard.png` — Farm Command Center, 8 KPI cards, quick actions bar, and pond snapshots
- `screenshots/02_ponds_command_center.png` — Pond inventory, dimensions, water source tags, and filters
- `screenshots/03_water_quality_matrix.png` — Physicochemical parameter matrix (pH, DO, Temp, Turbidity, Ammonia)
- `screenshots/04_fish_growth_analytics.png` — Fish stocking batches, species registry, and calculated biomass
- `screenshots/05_feeding_and_inventory.png` — Daily feed applications, biomass ration model variance, and warehouse stock
- `screenshots/06_ai_intelligence_center.png` — AquaMitra AI Companion chat and categorized insights
- `screenshots/07_financial_management.png` — Farm finances ledger, expenses, and Estimated Net Difference
- `screenshots/mobile_01_overview.png` — Responsive mobile layout with swipeable quick action bar and 2-column KPI grid

---

## 7. License & Credits

- **Student Developer:** CSE Community Service Project Team
- **Institution:** Department of Computer Science & Engineering
- **Advisory:** Built in accordance with practical Andhra Pradesh freshwater fishery standards (Krishna-Godavari delta).
