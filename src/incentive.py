"""P1: baseline-relative building ranking. Shows saved vs OWN baseline per occupant. No behaviour change is measured."""
import pandas as pd

from .pipeline import RAW, load_processed

REGIME = {"working": "working", "exam": "exam", "weekend": "weekend", "holiday": "weekend", "semester_break": "break"}


def ranking():
    _, _, d = load_processed()
    cal = pd.read_excel(RAW / "calendar.xlsx")[["date", "day_type"]]
    d = d.merge(cal, on="date", how="left")
    d["regime"] = d.day_type.map(REGIME)
    tr, te = d[d.date < "2026-09-18"], d[d.date >= "2026-09-18"]
    base = tr[~tr.outlier_elec].groupby(["building_id", "regime"]).electricity_kwh.median().rename("base").reset_index()
    te = te.merge(base, on=["building_id", "regime"], how="left")
    te = te[~te.outlier_elec & te.electricity_kwh.notna() & te.base.notna()]
    out = []
    for bid, g in te.groupby("building_id"):
        saved = float((g.base - g.electricity_kwh).sum())
        occ = float(g.occupancy_avg.mean())
        out.append({"building_id": bid, "saved_kwh_vs_own_baseline": round(saved, 1), "avg_occupancy": round(occ),
                    "saved_per_occupant": round(saved / occ, 2) if occ else None,
                    "note": "no behaviour change measured: baseline comparison only"})
    return sorted(out, key=lambda r: -(r["saved_per_occupant"] or 0))


if __name__ == "__main__":
    for r in ranking():
        print(r)
