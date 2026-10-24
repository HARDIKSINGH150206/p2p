"""Outage Drill: knock a building offline for N hours using real data as hidden truth, impute, then reconcile.

Headline imputer = day-type hourly profile (built from TRAIN days only) scaled to the VISIBLE hours of the same day.
No hidden-hour information is used. 'best_case_daily_total' additionally uses the daily summary total and is
labelled as what you get once the daily summary arrives after reconnect.
"""
import numpy as np
import pandas as pd

from .pipeline import load_processed
TEST_START = pd.Timestamp("2026-09-18")  # same train/test split as forecast.py

REGIME = {"working": "working", "exam": "exam", "weekend": "weekend", "holiday": "weekend", "semester_break": "break"}
_cache = {}


def _data():
    if "h" not in _cache:
        h, _, d = load_processed()
        h = h.copy()
        h["regime"] = h.day_type.map(REGIME)
        _cache.update(h=h, d=d)
    return _cache["h"], _cache["d"]


def _profile(h, bid):
    tr = h[(h.building_id == bid) & (h.timestamp < TEST_START) & (~h.missing)]
    prof = tr.groupby(["regime", "hour"]).electricity_kwh.mean()
    allp = tr.groupby("hour").electricity_kwh.mean()
    return prof, allp


def _prof_vec(prof, allp, regime, hours):
    return np.array([prof.get((regime, hr), allp.get(hr, np.nan)) for hr in hours], dtype=float)


def _err(actual, est):
    actual, est = np.asarray(actual, float), np.asarray(est, float)
    mae = float(np.mean(np.abs(actual - est)))
    nz = actual > 0
    mape = float(np.mean(np.abs(actual[nz] - est[nz]) / actual[nz])) if nz.any() else float("nan")
    return {"mae": round(mae, 3), "mape": round(mape, 4)}


def _one(h, d, bid, start, hours):
    prof, allp = _profile(h, bid)
    g = h[h.building_id == bid].set_index("timestamp").sort_index()
    hidden_idx = pd.date_range(pd.Timestamp(start), periods=hours, freq="h")
    hid = g.loc[g.index.intersection(hidden_idx)]
    hid = hid[~hid.missing]  # can only score hours that were really observed
    if len(hid) == 0:
        raise ValueError("no observed hours in window")
    est = {k: [] for k in ["profile_scaled_visible", "flat_visible_mean", "same_hours_last_week", "unscaled_profile", "best_case_daily_total"]}
    actual, rows = [], []
    for date, hh in hid.groupby("date"):
        day = g[g.date == date]
        vis = day[(~day.index.isin(hidden_idx)) & (~day.missing)]
        regime = hh.regime.iloc[0]
        p_h = _prof_vec(prof, allp, regime, hh.hour.to_numpy())
        p_v = _prof_vec(prof, allp, regime, vis.hour.to_numpy())
        ratio = vis.electricity_kwh.sum() / p_v.sum() if len(vis) and p_v.sum() > 0 else 1.0
        scaled = p_h * ratio
        flat = np.full(len(hh), vis.electricity_kwh.mean() if len(vis) else p_h.mean())
        wk = g.electricity_kwh_filled.reindex(hh.index - pd.Timedelta(hours=168)).to_numpy()
        tot = d[(d.building_id == bid) & (d.date == date)].electricity_kwh
        if len(tot) and not np.isnan(tot.iloc[0]) and p_h.sum() > 0:
            best = p_h / p_h.sum() * max(tot.iloc[0] - vis.electricity_kwh.sum(), 0)
        else:
            best = scaled
        est["profile_scaled_visible"] += list(scaled); est["flat_visible_mean"] += list(flat)
        est["same_hours_last_week"] += list(wk); est["unscaled_profile"] += list(p_h); est["best_case_daily_total"] += list(best)
        actual += list(hh.electricity_kwh)
        for t, a, e, ra in zip(hh.index, hh.electricity_kwh, scaled, hh.received_at):
            rows.append({"timestamp": str(t)[:16], "actual": round(float(a), 2), "estimate": round(float(e), 2)})
    errors = {k: _err(actual, np.nan_to_num(v, nan=np.nanmean(actual))) for k, v in est.items()}
    return rows, errors


def run_drill(building_id: str, start: str, hours: int = 6):
    h, d = _data()
    rows, errors = _one(h, d, building_id, start, hours)
    ranked = sorted(errors.items(), key=lambda kv: kv[1]["mae"])
    return {"building_id": building_id, "start": start, "hours": hours, "hidden": rows, "errors": errors,
            "best_honest_method": next(k for k, _ in ranked if k != "best_case_daily_total"),
            "notes": {"best_case_daily_total": "best case once the daily summary arrives after reconnect (uses hidden-hour total)",
                      "profile_source": "day-type hourly profile from days before 2026-09-18 only"}}


def benchmark(building_id: str, hours: int = 6, start_hour: int = 10):
    """Average error over every test-period day for one building (credibility check for the headline number)."""
    h, d = _data()
    days = sorted(h[(h.timestamp >= TEST_START)].date.unique())
    acc = {}
    n = 0
    for day in days:
        try:
            _, e = _one(h, d, building_id, f"{day} {start_hour:02d}:00", hours)
        except ValueError:
            continue
        n += 1
        for k, v in e.items():
            acc.setdefault(k, []).append(v)
    out = {k: {"mae": round(float(np.mean([x["mae"] for x in v])), 3),
               "mape": round(float(np.nanmean([x["mape"] for x in v])), 4)} for k, v in acc.items()}
    return {"building_id": building_id, "hours": hours, "start_hour": start_hour, "n_windows": n, "mean_errors": out}


if __name__ == "__main__":
    import json
    r = run_drill("B04", "2026-10-08 10:00", 6)
    print(json.dumps(r["errors"], indent=1), r["best_honest_method"])
    for b in ["B04", "B07", "B03"]:
        print(json.dumps(benchmark(b)))
