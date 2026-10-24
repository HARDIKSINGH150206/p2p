"""FastAPI backend. Run: uvicorn src.api:app --reload. Serves JSON under /api and the page at /."""
import json
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import pipeline

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
app = FastAPI(title="CircuGrid Brief")


@app.on_event("startup")
def _ensure_data():
    if not (pipeline.PROC / "hourly_clean.csv").exists():
        pipeline.build()


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


@app.get("/")
def index():
    return FileResponse(WEB / "index.html")


if WEB.exists():
    app.mount("/static", StaticFiles(directory=WEB), name="static")
