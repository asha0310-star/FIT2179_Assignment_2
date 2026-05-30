"""
Generate the cleaned CSV files used by the Vega-Lite charts.

The project intentionally keeps the final CSVs small for GitHub Pages. Most
series come directly from downloaded CSV/XLSX files. MPOB PDF table values that
are used in charts are typed below and cited in README.md.

Usage:
    python3 -m pip install -r requirements.txt
    python3 wrangle.py
"""

from pathlib import Path

import pandas as pd

RAW = Path("raw")
OUT = Path("data")
OUT.mkdir(exist_ok=True)

PALM_OWID = RAW / "palm-oil-production(Our World in Data).csv"
LANDUSE = RAW / "land-use-palm-oil.csv"
CPO_WIDE = RAW / "CPO Production by Country.csv"
GFW = RAW / "Global Forest Watch Data.xlsx"

PALM_ENTITIES = [
    "Malaysia",
    "Indonesia",
    "Thailand",
    "Colombia",
    "Nigeria",
    "Papua New Guinea",
    "Honduras",
    "Ghana",
    "World",
]

AGGREGATE_CODES = {
    "OWID_AFR",
    "OWID_ASI",
    "OWID_EUR",
    "OWID_NAM",
    "OWID_SAM",
    "OWID_WRL",
    "OWID_OCE",
    "OWID_LIC",
    "OWID_LMC",
    "OWID_UMC",
    "OWID_HIC",
}

# MPOB overview reports, typed from published tables.
PLANTED_AREA_MHA = {
    2000: 3.38,
    2001: 3.50,
    2002: 3.67,
    2003: 3.80,
    2004: 3.88,
    2005: 4.05,
    2006: 4.17,
    2007: 4.30,
    2008: 4.49,
    2009: 4.69,
    2010: 4.85,
    2011: 5.00,
    2012: 5.08,
    2013: 5.23,
    2014: 5.39,
    2015: 5.64,
    2016: 5.74,
    2017: 5.81,
    2018: 5.85,
    2019: 5.90,
    2020: 5.87,
    2021: 5.74,
    2022: 5.67,
    2023: 5.65,
    2024: 5.61,
    2025: 5.70005,
}

CPO_PRODUCTION_MT = {
    2000: 10.842095,
    2001: 11.804000,
    2002: 11.909300,
    2003: 13.354800,
    2004: 13.976200,
    2005: 14.961700,
    2006: 15.880700,
    2007: 15.823745,
    2008: 17.734440,
    2009: 17.564936,
    2010: 16.993716,
    2011: 18.911520,
    2012: 18.785030,
    2013: 19.216460,
    2014: 19.667016,
    2015: 19.961580,
    2016: 17.319176,
    2017: 19.919332,
    2018: 19.516140,
    2019: 19.858368,
    2020: 19.140612,
    2021: 18.116354,
    2022: 18.453420,
    2023: 18.551950,
    2024: 19.338266,
    2025: 20.283475,
}

MALAYSIA_KPI = [
    (2023, 18551950, 5652569, 15.79, 3809.50),
    (2024, 19338266, 5612852, 16.70, 4179.50),
    (2025, 20283475, 5700050, 17.77, 4292.50),
]

REGIONAL_CPO_2025 = [
    ("Peninsular Malaysia", 2543636, 11376845, 4.0, 102.5),
    ("Sabah", 1496558, 4410291, 5.8, 117.0),
    ("Sarawak", 1659857, 4496339, 2.5, 113.5),
]

TOP_IMPORTERS_2025 = [
    ("India", 2660000, 17.4, 2.66, 1),
    ("Kenya", 1210000, 7.9, 1.21, 2),
    ("European Union", 1030000, 6.8, 1.03, 3),
    ("China", 900000, 5.9, 0.90, 4),
    ("Türkiye", 750000, 4.9, 0.75, 5),
    ("Philippines", 720000, 4.7, 0.72, 6),
    ("Japan", 590000, 3.9, 0.59, 7),
]


def write_palm_production() -> None:
    print("1/9 palm_production_long.csv")
    df = pd.read_csv(PALM_OWID)
    df[df["Entity"].isin(PALM_ENTITIES)].to_csv(OUT / "palm_production_long.csv", index=False)


def write_cpo_by_country() -> None:
    print("2/9 cpo_by_country_long.csv")
    df = pd.read_csv(CPO_WIDE, skiprows=1)
    long = df.melt(id_vars="Period", var_name="Country", value_name="Production_kt")
    long.dropna(subset=["Production_kt"]).to_csv(OUT / "cpo_by_country_long.csv", index=False)


def write_landuse_slope() -> None:
    print("3/9 landuse_slope.csv")
    df = pd.read_csv(LANDUSE)
    df = df[df["Year"].isin([1961, 2023])]
    real = df[~df["Code"].isin(AGGREGATE_CODES) & df["Code"].notna()]
    top10 = (
        real[real["Year"] == 2023]
        .nlargest(10, "Palm fruit oil - Area harvested (hectares)")["Entity"]
        .tolist()
    )
    keep = set(top10) | {"Malaysia", "Indonesia"}
    real[real["Entity"].isin(keep)].to_csv(OUT / "landuse_slope.csv", index=False)


def write_forest_loss() -> pd.DataFrame:
    print("4/9 forest loss CSVs")
    gfw = pd.read_excel(GFW, sheet_name="Subnational 1 tree cover loss")
    gfw = gfw[gfw["threshold"] == 30].copy()
    year_cols = [c for c in gfw.columns if str(c).startswith("tc_loss_ha_")]

    intensity = gfw.rename(
        columns={"subnational1": "state", "extent_2000_ha": "tree_cover_extent_2000"}
    ).copy()
    intensity["total_loss_2001_2024"] = intensity[year_cols].sum(axis=1)
    intensity["loss_intensity_pct"] = (
        intensity["total_loss_2001_2024"] / intensity["tree_cover_extent_2000"] * 100
    ).round(2)
    intensity = intensity[
        ["state", "total_loss_2001_2024", "tree_cover_extent_2000", "loss_intensity_pct"]
    ].sort_values("loss_intensity_pct", ascending=False)
    intensity.to_csv(OUT / "state_loss_intensity.csv", index=False)
    long = gfw.melt(
        id_vars=["subnational1"],
        value_vars=year_cols,
        var_name="year_col",
        value_name="tc_loss_ha",
    )
    long["year"] = long["year_col"].str.replace("tc_loss_ha_", "").astype(int)
    long = long.rename(columns={"subnational1": "state"})[["state", "year", "tc_loss_ha"]]
    long.to_csv(OUT / "forest_loss_by_state_long.csv", index=False)

    totals = (
        long.groupby("state", as_index=False)["tc_loss_ha"]
        .sum()
        .rename(columns={"tc_loss_ha": "total_loss_2001_2024"})
        .sort_values("total_loss_2001_2024", ascending=False)
    )
    totals.to_csv(OUT / "forest_loss_state_totals.csv", index=False)
    return long


def write_area_loss_and_economy(forest_loss_long: pd.DataFrame) -> None:
    print("5/9 area_vs_loss_yearly.csv and malaysia_economy_yearly.csv")
    annual = (
        forest_loss_long.groupby("year", as_index=False)["tc_loss_ha"]
        .sum()
        .rename(columns={"tc_loss_ha": "forest_loss_ha"})
    )
    annual["forest_loss_kha"] = (annual["forest_loss_ha"] / 1000).round(2)
    annual["planted_area_Mha"] = annual["year"].map(PLANTED_AREA_MHA)
    annual[["year", "planted_area_Mha", "forest_loss_kha"]].dropna().to_csv(
        OUT / "area_vs_loss_yearly.csv", index=False
    )

    export_value = {
        2001: 14.4,
        2002: 14.2,
        2003: 19.0,
        2004: 22.5,
        2005: 24.4,
        2006: 31.8,
        2007: 45.6,
        2008: 65.2,
        2009: 49.6,
        2010: 59.8,
        2011: 80.4,
        2012: 71.5,
        2013: 61.4,
        2014: 63.6,
        2015: 60.2,
        2016: 67.6,
        2017: 77.8,
        2018: 67.5,
        2019: 64.8,
        2020: 73.3,
        2021: 108.0,
        2022: 137.9,
        2023: 80.6,
        2024: 73.0,
    }
    econ = annual[annual["year"].between(2001, 2024)].copy()
    econ["cpo_production_Mt"] = econ["year"].map(CPO_PRODUCTION_MT)
    econ["export_value_RMbn"] = econ["year"].map(export_value)
    econ = econ[["year", "cpo_production_Mt", "planted_area_Mha", "forest_loss_kha", "export_value_RMbn"]]
    econ.dropna().round({"cpo_production_Mt": 3, "forest_loss_kha": 2}).to_csv(
        OUT / "malaysia_economy_yearly.csv", index=False
    )


def write_malaysia_yearly() -> None:
    print("6/9 malaysia_yearly.csv and production_area_index.csv")
    rows = [
        (year, CPO_PRODUCTION_MT[year], PLANTED_AREA_MHA[year])
        for year in range(2000, 2026)
        if year in CPO_PRODUCTION_MT and year in PLANTED_AREA_MHA
    ]
    yearly = pd.DataFrame(rows, columns=["year", "cpo_production_Mt", "planted_area_Mha"])
    yearly.to_csv(OUT / "malaysia_yearly.csv", index=False)

    index = yearly[yearly["year"] >= 2001].copy()
    index["cpo_production_t"] = (index["cpo_production_Mt"] * 1_000_000).round().astype(int)
    index["planted_area_ha"] = (index["planted_area_Mha"] * 1_000_000).round().astype(int)
    base = index[index["year"] == 2001].iloc[0]
    index["production_index"] = (index["cpo_production_t"] / base["cpo_production_t"] * 100).round(2)
    index["area_index"] = (index["planted_area_ha"] / base["planted_area_ha"] * 100).round(2)
    index[["year", "cpo_production_t", "planted_area_ha", "production_index", "area_index"]].to_csv(
        OUT / "production_area_index.csv", index=False
    )


def write_2025_tables() -> None:
    print("7/9 MPOB 2025 tables")
    pd.DataFrame(
        REGIONAL_CPO_2025,
        columns=["region", "planted_area_ha", "cpo_production_t", "latitude", "longitude"],
    ).to_csv(OUT / "state_cpo_2025.csv", index=False)

    pd.DataFrame(
        [(c, t, s) for c, t, s, _v, _o in TOP_IMPORTERS_2025],
        columns=["country", "tonnes", "share_pct"],
    ).to_csv(OUT / "top_importers_2025.csv", index=False)

    flow_rows = []
    for country, _tonnes, share_pct, volume_mt, order in TOP_IMPORTERS_2025:
        flow_rows.append((country, volume_mt, share_pct, "source", 0, 4.0, 0))
        flow_rows.append((country, volume_mt, share_pct, "dest", 100, order, 1))
    pd.DataFrame(flow_rows, columns=["country", "volume_Mt", "share_pct", "point", "x", "y", "order"]).to_csv(
        OUT / "imports_flows.csv", index=False
    )


def write_kpi() -> None:
    print("8/9 malaysia_palmoil_kpi.csv")
    pd.DataFrame(
        MALAYSIA_KPI,
        columns=["year", "cpo_production_t", "planted_area_ha", "ffb_yield_t_ha", "avg_cpo_price_rm_t"],
    ).to_csv(OUT / "malaysia_palmoil_kpi.csv", index=False)


def main() -> None:
    write_palm_production()
    write_cpo_by_country()
    write_landuse_slope()
    forest_loss_long = write_forest_loss()
    write_area_loss_and_economy(forest_loss_long)
    write_malaysia_yearly()
    write_2025_tables()
    write_kpi()
    print("9/9 done")


if __name__ == "__main__":
    main()
