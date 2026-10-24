"""Per-building ridge forecast of hourly electricity, 6 h and 12 h ahead, vs two naive baselines.

Time-ordered split: train on target times before TEST_START, evaluate on or after it.
"""
import time
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .pipeline import load_processed

TEST_START = pd.Timestamp("2026-09-18")
WINDOWS = {
    "all_test": (pd.Timestamp("2026-09-18"), pd.Timestamp("2026-10-18")),
    "alumni_19sep": (pd.Timestamp("2026-09-19"), pd.Timestamp("2026-09-20")),
    "exam_28sep_9oct": (pd.Timestamp("2026-09-28"), pd.Timestamp("2026-10-10")),
}
HORIZONS = (6, 12)
DAY_TYPES = ["working", "weekend", "holiday", "exam", "semester_break"]
FEATURES = ["hsin", "hcos", "dow", "temp", "has_event", "elec_t", "foot_t", "lag_week", "lag_day"] + ["dt_" + d for d in DAY_TYPES]


def _frame(h, bid, horizon):
    """One row per origin time t; target is electricity at t+horizon. All features are known at t."""
    g = h[h.building_id == bid].sort_values("timestamp").reset_index(drop=True)
    e = g["electricity_kwh_filled"].to_numpy()
    f = g["footfall_filled"].to_numpy()
    n = len(g)
    t_idx = np.arange(n)
    tgt = t_idx + horizon
    ok = (tgt < n) & (tgt - 168 >= 0)
    t_idx, tgt = t_idx[ok], tgt[ok]
    tg = g.iloc[tgt]
    X = pd.DataFrame({
        "hsin": np.sin(2 * np.pi * tg.hour.to_numpy() / 24), "hcos": np.cos(2 * np.pi * tg.hour.to_numpy() / 24),
        "dow": tg.timestamp.dt.day_of_week.to_numpy(), "temp": tg.avg_temp_c.to_numpy(),
        "has_event": tg.event.notna().astype(int).to_numpy(),
        "elec_t": e[t_idx], "foot_t": f[t_idx], "lag_week": e[tgt - 168], "lag_day": e[tgt - 24],
    })
    for d in DAY_TYPES:
        X["dt_" + d] = (tg.day_type.to_numpy() == d).astype(int)
    X["target_time"] = tg.timestamp.to_numpy()
    X["y"] = e[tgt]
    X["observed"] = (~tg.missing).to_numpy()  # score only on really-observed target hours
    return X


def _scores(y, p):
    err = np.abs(y - p)
    return float(err.mean()), float(err.sum() / np.abs(y).sum())


def run_forecast(include_hgb_timing=True):
    h, _, _ = load_processed()
    metrics, series, resid_spread = [], {}, {}
    fit_time = {"ridge": None, "hgb": None}
    for bid in sorted(h.building_id.unique()):
        for hz in HORIZONS:
            X = _frame(h, bid, hz)
            tr = X[(X.target_time < TEST_START)]
            te = X[(X.target_time >= TEST_START)]
            m = make_pipeline(StandardScaler(), Ridge(alpha=10.0))
            t0 = time.perf_counter()
            m.fit(tr[FEATURES], tr.y)
            ridge_t = time.perf_counter() - t0
            if fit_time["ridge"] is None:
                fit_time["ridge"] = round(ridge_t, 4)
            if include_hgb_timing and fit_time["hgb"] is None:
                t0 = time.perf_counter()
                HistGradientBoostingRegressor(max_iter=100).fit(tr[FEATURES], tr.y)
                fit_time["hgb"] = round(time.perf_counter() - t0, 4)
            te = te.assign(ridge=m.predict(te[FEATURES]))
            resid_spread[(bid, hz)] = float(np.median(np.abs(tr.y - m.predict(tr[FEATURES]))))
            for wname, (a, b) in WINDOWS.items():
                w = te[(te.target_time >= a) & (te.target_time < b) & te.observed]
                if len(w) == 0:
                    continue
                for mname, col in [("ridge", "ridge"), ("naive_same_hour_last_week", "lag_week"), ("naive_same_hour_yesterday", "lag_day")]:
                    mae, wape = _scores(w.y.to_numpy(), w[col].to_numpy())
                    metrics.append({"building_id": bid, "horizon_h": hz, "model": mname, "window": wname,
                                    "mae": round(mae, 2), "wape": round(wape, 4), "n": int(len(w))})
            if bid == "B07" and hz == 6:
                w = te[(te.target_time >= WINDOWS["alumni_19sep"][0]) & (te.target_time < WINDOWS["alumni_19sep"][1])]
                series = {"building_id": "B07", "horizon_h": 6,
                          "timestamps": [str(t)[:16] for t in w.target_time],
                          "actual": [round(v, 2) for v in w.y], "forecast": [round(v, 2) for v in w.ridge],
                          "naive_week": [round(v, 2) for v in w.lag_week], "naive_day": [round(v, 2) for v in w.lag_day]}
    # which model wins per building (6 h, all_test)
    best = {}
    for bid in sorted(h.building_id.unique()):
        rows = [r for r in metrics if r["building_id"] == bid and r["horizon_h"] == 6 and r["window"] == "all_test"]
        best[bid] = min(rows, key=lambda r: r["wape"])["model"]
    return {"metrics": metrics, "fit_time_s": fit_time, "b07_19sep": series, "best_model_6h_all_test": best,
            "split": {"train": "target time < 2026-09-18", "test": "2026-09-18 .. 2026-10-17"}}


if __name__ == "__main__":
    r = run_forecast()
    df = pd.DataFrame(r["metrics"])
    pd.set_option("display.width", 200)
    print(r["fit_time_s"], r["best_model_6h_all_test"])
    print(df[(df.window == "all_test")].pivot_table(index=["building_id", "horizon_h"], columns="model", values="wape").round(3))
    print(df[(df.window == "alumni_19sep") & (df.building_id == "B07")].round(3))
    print(df[(df.window == "exam_28sep_9oct")].pivot_table(index=["building_id", "horizon_h"], columns="model", values="wape").round(3))
