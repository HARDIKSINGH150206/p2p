"""FastAPI backend. Run: uvicorn src.api:app --reload. Serves JSON under /api and the page at /."""
import json
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import pipeline

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
app = FastAPI(title="CircuGrid Brief")
app.add_middleware(GZipMiddleware, minimum_size=800)


@app.on_event("startup")
def _ensure_data():
    if not (pipeline.PROC / "hourly_clean.csv").exists():
        pipeline.build()
    import threading

    def warm():  # compute the slow modules once so the first page load is fast
        for n in ("brief", "forecast", "impact", "classifier", "incentive"):
            try:
                _cached(n)
            except Exception:
                pass
    threading.Thread(target=warm, daemon=True).start()


@app.get("/api/health")
def health():
    return {"ok": True, "processed": (pipeline.PROC / "hourly_clean.csv").exists()}


@lru_cache(maxsize=None)
def _cached(name):
    if name == "brief":
        from .insights import brief
        return brief(top=12)
    if name == "forecast":
        from .forecast import run_forecast
        return run_forecast()
    if name == "impact":
        from .impact import impact
        return impact()
    if name == "classifier":
        from .classifier import run_classifier
        return run_classifier()
    if name == "incentive":
        from .incentive import ranking
        return ranking()
    raise KeyError(name)


def _serve(name):
    try:
        return _cached(name)
    except Exception as e:  # never crash the demo: surface the error in the payload
        return {"error": f"{type(e).__name__}: {e}"}


@app.get("/api/stats")
def stats():
    p = pipeline.PROC / "pipeline_stats.json"
    return json.loads(p.read_text()) if p.exists() else {}


@app.get("/api/brief")
def brief():
    return _serve("brief")


@app.get("/api/forecast")
def forecast():
    return _serve("forecast")


@app.get("/api/impact")
def impact():
    return _serve("impact")


@app.get("/api/classifier")
def classifier():
    return _serve("classifier")


@app.get("/api/incentive")
def incentive():
    return _serve("incentive")


class DrillReq(BaseModel):
    building_id: str = "B04"
    start: str = "2026-10-08 10:00"
    hours: int = 6


@app.post("/api/drill")
def drill(req: DrillReq):
    from .drill import run_drill, benchmark
    try:
        r = run_drill(req.building_id, req.start, req.hours)
        r["benchmark"] = benchmark(req.building_id, req.hours)
        return r
    except Exception as e:
        raise HTTPException(400, f"{type(e).__name__}: {e}")


@app.get("/api/timeseries")
def timeseries():
    """Daily series per building plus real events (staff notes and calendar events) for annotation."""
    import pandas as pd
    _, m, d = pipeline.load_processed()
    cal = pd.read_excel(pipeline.RAW / "calendar.xlsx")
    dates = sorted(d.date.unique())
    metrics = ["electricity_kwh", "water_litres", "solar_generation_kwh", "composted_kg", "recycled_kg", "landfill_kg", "wet_organic_kg", "occupancy_avg"]
    out = {}
    for bid, g in d.groupby("building_id"):
        g = g.set_index("date").reindex(dates)
        out[bid] = {k: [None if pd.isna(v) else round(float(v), 2) for v in g[k]] for k in metrics}
        out[bid]["outlier"] = [bool(x) if not pd.isna(x) else False for x in g.outlier_elec]
    ev = []
    for _, r in m[m.stream == "note"].iterrows():
        ev.append({"date": r.date, "building_id": r.building_id, "kind": "note", "cause": r.cause, "label": r.note})
    for _, r in cal[cal.event.notna()].iterrows():
        ev.append({"date": r.date, "building_id": None, "kind": "calendar", "cause": r.day_type, "label": r.event})
    days = [{"date": r.date, "day_type": r.day_type, "rain": float(r.rainfall_mm), "temp": float(r.avg_temp_c)} for _, r in cal.iterrows()]
    return {"dates": dates, "buildings": out, "events": ev, "days": days}


@app.get("/api/buildings")
def buildings():
    import pandas as pd
    _, _, d = pipeline.load_processed()
    b = pd.read_excel(pipeline.RAW / "buildings.xlsx")
    g = d.groupby("building_id").agg(electricity_kwh=("electricity_kwh", "sum"), solar_kwh=("solar_generation_kwh", "sum"),
                                     wet_organic_kg=("wet_organic_kg", "sum"), composted_kg=("composted_kg", "sum"), recycled_kg=("recycled_kg", "sum"),
                                     landfill_kg=("landfill_kg", "sum"), water_litres=("water_litres", "sum")).reset_index()
    out = b.merge(g, on="building_id")
    tot = out.electricity_kwh.sum()
    out["electricity_share_pct"] = (out.electricity_kwh / tot * 100).round(1)
    return out.round(0).assign(electricity_share_pct=out.electricity_share_pct).to_dict("records")


@app.get("/")
def index():
    return FileResponse(WEB / "index.html")


@app.get("/app")
def workspace():
    return FileResponse(WEB / "app.html")


if WEB.exists():
    app.mount("/static", StaticFiles(directory=WEB), name="static")
