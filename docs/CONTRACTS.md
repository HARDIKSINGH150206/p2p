# Contracts between phases
One-line: the function and JSON shapes both sides code against, so work can run in parallel.
Last updated: 12:35 IST

Shared foundation (on `main`): `src/pipeline.py` writes `data/processed/{hourly_clean,daily_clean,manual_clean}.csv` and `pipeline_stats.json`; `load_processed()` returns `(hourly, manual, daily)` DataFrames.
- hourly_clean: timestamp, building_id, electricity_kwh, water_litres, solar_generation_kwh, footfall, `*_filled`, missing, day_type, event, avg_temp_c, rainfall_mm, humidity_pct, hour, date
- manual_clean: building_id (aliased), stream, value_std, rejected, date, note, cause
- daily_clean: daily_summary + `outlier_elec`

All modules return plain dicts/lists (JSON-serialisable) so the API can pass them through.

## Hardik → API
- `src/forecast.py::run_forecast() -> {"metrics":[{building_id,horizon_h,model,window,mae,wape}], "fit_time_s":{"ridge":float,"hgb":float}, "b07_19sep":{"timestamps":[...],"actual":[...],"forecast":[...],"naive_week":[...],"naive_day":[...]}}`
- `src/insights.py::brief() -> {"cards":[{id,building_id,date_range,title,cause,evidence,kwh,rs,co2_kg,action,confidence}], "attribution_counts":{"attributed":int,"unexplained":int}}`
- `src/drill.py::run_drill(building_id:str, start:str, hours:int) -> {"hidden":[{timestamp,actual,estimate}], "errors":{"profile_scaled_visible":{mae,mape},"flat_visible_mean":{...},"same_hours_last_week":{...},"unscaled_profile":{...},"best_case_daily_total":{...}}}`

## Jhashank → API
- `src/classifier.py::run_classifier() -> {"accuracy":float,"per_class":{cls:{precision,recall,support}},"confusion":{labels:[...],matrix:[[...]]},"latency_ms":{"p50":float,"p95":float},"routing":{"test_counts":{cls:int},"compost_eligible_buildings":[...]},"evaluated_on":"20% stratified hold-out of waste_events_train"}`; also writes `waste_events_test_predictions.csv` (event_id, predicted_class) at repo root of `data/processed/`.
- `src/impact.py::impact() -> {"baseline":{...},"events":[{id,label,building_id,kwh,rs,co2_kg,litres,kg,assumption}], "assumptions":{co2_kg_per_kwh:0.70,rs_per_kwh:8,kwh_per_1000l:0.85,compost_ratio:4}}`
- `src/incentive.py::ranking() -> [{building_id,saved_per_occupant,note:"no behaviour change measured"}]` (P1)

## API endpoints (`src/api.py`, FastAPI)
GET `/api/brief`, `/api/forecast`, `/api/impact`, `/api/classifier`, `/api/stats`; POST `/api/drill` body `{building_id,start,hours}`. Until a module exists, the endpoint returns a stub with `"stub": true`; swap in the real call when the module merges. Static page at `/` (`web/index.html`).
