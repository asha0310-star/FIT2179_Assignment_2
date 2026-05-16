"""
wrangle.py — turns the raw source files into the cleaned CSVs the
Vega-Lite charts expect. Run once before building charts; re-run if
the raw data changes.

Usage (from inside the repo folder):
    python wrangle.py
"""

import os
import pandas as pd

# ---------------------------------------------------------------------
# CONFIG: put the raw downloads in a folder called 'raw/' next to this
# script. Adjust paths if you keep them elsewhere.
# ---------------------------------------------------------------------
RAW = "raw"
OUT = "data"
os.makedirs(OUT, exist_ok=True)

PALM_OWID   = f"{RAW}/palm-oil-production(Our World in Data).csv"
LANDUSE     = f"{RAW}/land-use-palm-oil.csv"
CPO_WIDE    = f"{RAW}/CPO Production by Country.csv"
GFW         = f"{RAW}/Global Forest Watch Data.xlsx"

# ---------------------------------------------------------------------
# 1) palm_production_long.csv
#    Filter OWID file to nine entities; keep schema as-is so the
#    chart JSONs reference the original column names.
# ---------------------------------------------------------------------
print("1/7  palm_production_long.csv")
df = pd.read_csv(PALM_OWID)
keep = ["Malaysia", "Indonesia", "Thailand", "Colombia",
        "Nigeria", "Papua New Guinea", "Honduras", "Ghana", "World"]
df = df[df["Entity"].isin(keep)]
df.to_csv(f"{OUT}/palm_production_long.csv", index=False)

# ---------------------------------------------------------------------
# 2) cpo_by_country_long.csv
#    Unpivot the CPO-by-country wide table to long format.
#    Note: the source file has a one-line title row above the header.
# ---------------------------------------------------------------------
print("2/7  cpo_by_country_long.csv")
df = pd.read_csv(CPO_WIDE, skiprows=1)              # skip "CPO Production..." title
long = df.melt(id_vars="Period",
               var_name="Country",
               value_name="Production_kt")
long = long.dropna(subset=["Production_kt"])
long.to_csv(f"{OUT}/cpo_by_country_long.csv", index=False)

# ---------------------------------------------------------------------
# 3) landuse_slope.csv
#    Only need 1961 + 2023 for the slope chart, top 10 producers + MY/ID.
# ---------------------------------------------------------------------
print("3/7  landuse_slope.csv")
df = pd.read_csv(LANDUSE)
df = df[df["Year"].isin([1961, 2023])]
# Find top 10 by 2023 area, ignoring aggregates
agg_codes = {"OWID_AFR", "OWID_ASI", "OWID_EUR", "OWID_NAM",
             "OWID_SAM", "OWID_WRL", "OWID_OCE"}
real = df[~df["Code"].isin(agg_codes) & df["Code"].notna()]
top10 = (real[real["Year"] == 2023]
         .nlargest(10, "Palm fruit oil - Area harvested (hectares)")["Entity"]
         .tolist())
# Always include Malaysia and Indonesia
keep = set(top10) | {"Malaysia", "Indonesia"}
slope = real[real["Entity"].isin(keep)]
slope.to_csv(f"{OUT}/landuse_slope.csv", index=False)

# ---------------------------------------------------------------------
# 4) forest_loss_by_state_long.csv
#    Read the GFW Subnational1 sheet, keep threshold=30 rows,
#    melt the tc_loss_ha_YYYY columns into year + tc_loss_ha.
# ---------------------------------------------------------------------
print("4/7  forest_loss_by_state_long.csv")
gfw = pd.read_excel(GFW, sheet_name="Subnational 1 tree cover loss")
gfw = gfw[gfw["threshold"] == 30]
year_cols = [c for c in gfw.columns if str(c).startswith("tc_loss_ha_")]
long = gfw.melt(id_vars=["subnational1"],
                value_vars=year_cols,
                var_name="year_col",
                value_name="tc_loss_ha")
long["year"] = long["year_col"].str.replace("tc_loss_ha_", "").astype(int)
long = long.rename(columns={"subnational1": "state"})
long = long[["state", "year", "tc_loss_ha"]]
long.to_csv(f"{OUT}/forest_loss_by_state_long.csv", index=False)

# ---------------------------------------------------------------------
# 5) forest_loss_state_totals.csv
#    Aggregate by state — used by both maps.
# ---------------------------------------------------------------------
print("5/7  forest_loss_state_totals.csv")
totals = (long.groupby("state", as_index=False)["tc_loss_ha"]
          .sum()
          .rename(columns={"tc_loss_ha": "total_loss_2001_2024"})
          .sort_values("total_loss_2001_2024", ascending=False))
totals.to_csv(f"{OUT}/forest_loss_state_totals.csv", index=False)

# ---------------------------------------------------------------------
# 6) area_vs_loss_yearly.csv
#    For the connected-scatter chart. National annual loss is
#    aggregated from GFW; planted area must be typed from MPOB.
#    Below is a sensible Malaysia area series in Mha — REPLACE with
#    the real MPOB-published values when you have them.
# ---------------------------------------------------------------------
print("6/7  area_vs_loss_yearly.csv")
annual = (long.groupby("year", as_index=False)["tc_loss_ha"].sum()
          .rename(columns={"tc_loss_ha": "forest_loss_ha"}))
annual["forest_loss_kha"] = (annual["forest_loss_ha"] / 1000).round(2)

# Planted area (Mha) by year — TYPE FROM MPOB REPORTS:
planted_area = {
    2001: 3.50, 2002: 3.67, 2003: 3.80, 2004: 3.88, 2005: 4.05,
    2006: 4.17, 2007: 4.30, 2008: 4.49, 2009: 4.69, 2010: 4.85,
    2011: 5.00, 2012: 5.08, 2013: 5.23, 2014: 5.39, 2015: 5.64,
    2016: 5.74, 2017: 5.81, 2018: 5.85, 2019: 5.90, 2020: 5.87,
    2021: 5.74, 2022: 5.67, 2023: 5.65, 2024: 5.61
}
annual["planted_area_Mha"] = annual["year"].map(planted_area)
annual = annual[["year", "planted_area_Mha", "forest_loss_kha"]].dropna()
annual.to_csv(f"{OUT}/area_vs_loss_yearly.csv", index=False)

# ---------------------------------------------------------------------
# 7) typed-out MPOB CSVs — straight from the 2024 Overview PDF.
# ---------------------------------------------------------------------
print("7/7  typed MPOB CSVs")

pd.DataFrame({
    "state":            ["Peninsular Malaysia", "Sabah", "Sarawak"],
    "planted_area_ha":  [2504786, 1483699, 1624366],
    "cpo_production_t": [10891417, 4274440, 4172409],
    "latitude":         [4.0, 5.5, 2.5],
    "longitude":        [102.5, 117.0, 113.5],
}).to_csv(f"{OUT}/state_cpo_2024.csv", index=False)

pd.DataFrame({
    "country":   ["India", "China", "European Union", "Kenya",
                  "Turkiye", "Philippines", "Japan"],
    "tonnes":    [3030000, 1390000, 1290000, 1260000, 910000, 690000, 600000],
    "share_pct": [17.9, 8.2, 7.7, 7.5, 5.4, 4.1, 3.6],
}).to_csv(f"{OUT}/top_importers_2024.csv", index=False)

pd.DataFrame({
    "year":              [2000, 2005, 2010, 2015, 2020, 2023, 2024],
    "cpo_production_Mt": [10.84, 14.96, 16.99, 19.96, 19.14, 18.55, 19.34],
    "planted_area_Mha":  [3.38, 4.05, 4.85, 5.64, 5.87, 5.65, 5.61],
}).to_csv(f"{OUT}/malaysia_yearly.csv", index=False)

# Regional production — placeholder values; replace with MPOB-published.
pd.DataFrame([
    ("Peninsular Malaysia", 2000, 8200000),
    ("Sabah",               2000, 2150000),
    ("Sarawak",             2000,  490000),
    ("Peninsular Malaysia", 2005, 9100000),
    ("Sabah",               2005, 4720000),
    ("Sarawak",             2005, 1140000),
    ("Peninsular Malaysia", 2010, 9800000),
    ("Sabah",               2010, 5860000),
    ("Sarawak",             2010, 1340000),
    ("Peninsular Malaysia", 2015, 10470000),
    ("Sabah",               2015, 5390000),
    ("Sarawak",             2015, 4100000),
    ("Peninsular Malaysia", 2020, 10130000),
    ("Sabah",               2020, 4410000),
    ("Sarawak",             2020, 4600000),
    ("Peninsular Malaysia", 2024, 10891417),
    ("Sabah",               2024, 4274440),
    ("Sarawak",             2024, 4172409),
], columns=["region", "year", "cpo_production_t"]
).to_csv(f"{OUT}/region_production_yearly.csv", index=False)

print("\nAll done. Check the data/ folder.")