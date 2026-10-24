# P2P 2026 — Predictive Circular-Resource Grid

**Prompt to Product (P2P) 2026** competition project: design and prototype an AI-driven
"Predictive Circular-Resource Grid" for an 8-building academic campus that forecasts and
manages **waste, water, and electricity** flows.

- **Problem:** *Predictive Circular-Resource Grid for a Multi-Building Campus*
- **Dataset:** Synthetic / hypothetical operational benchmark — 8 buildings, 120 days
  (20 Jun 2026 → 17 Oct 2026)
- **Core deliverable:** A working dashboard/product backed by real models, plus a
  step-by-step Prompt Workbook, a 3-page PDF report, and a 2.5-min video walkthrough.

## Problem statement (key constraints)

| # | Challenge | Requirement |
|---|-----------|-------------|
| 1 | Multi-modal sensor fusion | ≥3 heterogeneous, noisy, asynchronous sources; no discarded buildings |
| 2 | Real-time edge classification | ≥85% accuracy, 5+ waste classes, <2 s/event, no cloud GPU |
| 3 | Short-horizon forecasting | 6–12 h ahead demand/waste spikes, justified accuracy–compute trade-off |
| 4 | Intermittent connectivity | Local buffering, dedup, delay-free reconciliation |
| 5 | Root-cause attribution | Ranked, explainable action recommendations (not just dashboards) |
| 6 | Behavioural + economic loop | Gamification/credits with a defined measurement of impact |
| 7 | Cost & scale envelope | Stated per-building budget; scales 3 → 30+ buildings |
| 8 | Failure-mode awareness | ≥2 real failure modes with concrete mitigations |

## Repository layout

```
P2P/
├── Data/                    # raw competition datasets (xlsx)
├── Data_cleaning/           # EDA + cleaning pipeline, cleaned outputs
│   ├── eda_check.py         # integrity sweep (reproduce the EDA report)
│   └── data_pipeline.py     # steps 1-2: dedup, grid repair, alias/units, imputation
├── Docs/                    # problem statement, dataset guide, quality report
└── README.md
```

## Data files (raw, under `Data/`)

| File | Rows | Description |
|------|------|-------------|
| `Data/buildings.xlsx` | 8 | Building metadata: type, floors, area, capacity, solar & composter flags |
| `Data/calendar.xlsx` | 120 | Academic schedule (day types, events) + weather (temp, rain, humidity) |
| `Data/daily_summary.xlsx` | 960 | Per-building daily aggregates: occupancy, energy, water, waste streams, diversion |
| `Data/hourly_streams.xlsx` | 23,192 | Async hourly telemetry (kWh, water, solar, footfall) with gateway dropouts, burst retransmits & duplicates |
| `Data/manual_logs.xlsx` | 415 | Field logs with building-name aliases ("BH", "Boys Hostle"…) and mixed units (kWh/units, L/kL, kg/bags) |
| `Data/waste_events_train.xlsx` | 6,314 | Smart-bin events (5 sensors) with verified 6-class labels |
| `Data/waste_events_test.xlsx` | 1,601 | Unlabelled smart-bin events for evaluation / optional predictions file |

Cleaned analysis-ready tables and the cleaning log are produced by
`Data_cleaning/data_pipeline.py` into `Data_cleaning/cleaned/`
(see `Docs/DATA_QUALITY_REPORT.md` for the evidence behind every repair rule).

Waste categories: `food_organic`, `paper_cardboard`, `plastic`, `glass`, `metal`, `ewaste`.

Smart-bin sensors: `weight_g`, `moisture_pct`, `metal_signal`, `transparency`, `acoustic_hardness`.

Engineering constants: ₹8.00/kWh tariff · 0.70 kg CO₂/kWh · 0.85 kWh per 1,000 L water · 4:1 compost conversion.

## Roadmap

- [x] Dataset exploration & schema verification
- [ ] Data ingestion & cleaning pipeline (dedup, alias mapping, unit normalization)
- [ ] Waste-event classifier (edge-oriented, ≥85%)
- [ ] 6–12 h demand / waste-spike forecaster
- [ ] Root-cause anomaly attribution engine
- [ ] Circular-resource dashboard UI
- [ ] Cost envelope, scaling argument & failure modes (report)
- [ ] Prompt Workbook, final report PDF, video walkthrough
