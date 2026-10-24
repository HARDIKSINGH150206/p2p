"""Edge bin classifier: 6 waste classes from 5 sensor features. Small random forest, CPU only."""
import time
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline

from .pipeline import PROC, RAW

FEATURES = ["weight_g", "moisture_pct", "metal_signal", "transparency", "acoustic_hardness"]
_cache = {}


def run_classifier():
    if "r" in _cache:
        return _cache["r"]
    tr = pd.read_excel(RAW / "waste_events_train.xlsx")
    te = pd.read_excel(RAW / "waste_events_test.xlsx")
    X_tr, X_ho, y_tr, y_ho = train_test_split(tr[FEATURES], tr.category, test_size=0.2, stratify=tr.category, random_state=42)
    model = make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, n_jobs=1))
    t0 = time.perf_counter()
    model.fit(X_tr, y_tr)
    fit_s = time.perf_counter() - t0
    pred = model.predict(X_ho)
    labels = sorted(tr.category.unique())
    p, r, _, s = precision_recall_fscore_support(y_ho, pred, labels=labels, zero_division=0)
    # single-event latency (one row at a time, as an edge device would see it)
    lat = []
    rows = X_ho.head(200)
    for i in range(len(rows)):
        t0 = time.perf_counter()
        model.predict(rows.iloc[[i]])
        lat.append((time.perf_counter() - t0) * 1000)
    test_pred = model.predict(te[FEATURES])
    out = pd.DataFrame({"event_id": te.event_id, "predicted_class": test_pred})
    PROC.mkdir(parents=True, exist_ok=True)
    out.to_csv(PROC / "waste_events_test_predictions.csv", index=False)
    comp_b = ["B05", "B06", "B07"]  # buildings with has_composter = 1
    b = pd.read_excel(RAW / "buildings.xlsx")
    comp_b = b[b.has_composter == 1].building_id.tolist()
    food = te.assign(pred=test_pred)
    food = food[food.pred == "food_organic"]
    res = {
        "accuracy": round(float(accuracy_score(y_ho, pred)), 4),
        "per_class": {l: {"precision": round(float(p[i]), 3), "recall": round(float(r[i]), 3), "support": int(s[i])} for i, l in enumerate(labels)},
        "confusion": {"labels": labels, "matrix": confusion_matrix(y_ho, pred, labels=labels).tolist()},
        "latency_ms": {"p50": round(float(np.percentile(lat, 50)), 2), "p95": round(float(np.percentile(lat, 95)), 2)},
        "fit_time_s": round(fit_s, 2),
        "routing": {"test_counts": {k: int(v) for k, v in out.predicted_class.value_counts().items()},
                    "compost_eligible_buildings": comp_b,
                    "food_organic_events_in_composter_buildings": int(food.building_id.isin(comp_b).sum()),
                    "food_organic_events_without_composter": int((~food.building_id.isin(comp_b)).sum())},
        "evaluated_on": f"20% stratified hold-out of waste_events_train (n={len(y_ho)}); test file is unlabelled so no accuracy is claimed there",
        "n_train": int(len(y_tr)), "n_test_predicted": int(len(out)),
    }
    _cache["r"] = res
    return res


if __name__ == "__main__":
    import json
    r = run_classifier()
    print(r["accuracy"], r["latency_ms"], r["fit_time_s"])
    print(json.dumps(r["per_class"]))
    print(r["routing"])
