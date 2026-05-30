# Forests for Palm Oil — Malaysia's Trade-Off

FIT2179 Data Visualisation 2, Semester 1 2026. This single-page Vega-Lite story explains how Malaysia's palm oil economy connects to land expansion, tree-cover loss, and export demand.

## Domain, audience, and purpose

- **Domain:** Malaysia's palm oil industry and its environmental trade-off.
- **Audience:** A general Malaysian audience with no specialist statistics background.
- **Why:** Palm oil is economically important, but its landscape cost is uneven and difficult to understand from separate industry and forest datasets.
- **What:** The page combines palm oil production, planted-area, export, import-destination, and tree-cover-loss data.
- **How:** The story uses Munzer's What/Why/How framing through time-series charts, ranked bars, custom flow diagrams, a derived efficiency metric, a dual-direction trade-off chart, small multiples, and geographic maps.

## Assignment checklist

- Single scrollable web page: `index.html`.
- Vega-Lite JSON specifications are human-readable in `charts/`.
- Includes more than ten charts/diagrams, including two geographic maps.
- Total cleaned data plus chart specs is small enough for GitHub Pages loading.
- Uses multiple independent sources: Our World in Data, MPOB, and Global Forest Watch.
- AI use and data caveats are acknowledged in the page footer.

## Data sources

| Source                                                                                                                                               | Files used/generated                                                                                                                                                                | Purpose                                                                                                  |
| ---------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Our World in Data — Palm Oil (`raw/palm-oil-production(Our World in Data).csv`, `raw/land-use-palm-oil.csv`)                                         | `data/palm_production_long.csv`, `data/landuse_slope.csv`                                                                                                                           | Long-run global production and harvested-area context.                                                   |
| Malaysian Palm Oil Board overview reports (`raw/Annual Overview Reports Overview 2024.pdf` and public 2025 overview figures typed into `wrangle.py`) | `data/malaysia_yearly.csv`, `data/production_area_index.csv`, `data/malaysia_palmoil_kpi.csv`, `data/state_cpo_2025.csv`, `data/top_importers_2025.csv`, `data/imports_flows.csv`, `data/malaysia_economy_yearly.csv` | Malaysia production, planted area, regional 2025 production, export values, and top export destinations. |
| Global Forest Watch (`raw/Global Forest Watch Data.xlsx`)                                                                                            | `data/forest_loss_by_state_long.csv`, `data/forest_loss_state_totals.csv`, `data/state_loss_intensity.csv`, `data/area_vs_loss_yearly.csv`                                                                           | State and national tree-cover loss, 2001–2024.                                                           |
| Malaysia TopoJSON (`data/malaysia_states.topojson`)                                                                                                  | used directly by `charts/map08_choropleth_states.json` and `charts/map09_layered_map.json`                                                                                          | Geographic state boundaries for Vega-Lite maps.                                                          |

## Data caveats

- Global Forest Watch tree-cover loss is not identical to permanent deforestation. It can include timber harvest and plantation rotations.
- The project uses tree-cover loss and palm oil production together to show overlap and timing, not exact hectare-by-hectare causality.
- OWID's long-run production series currently ends at 2023, while MPOB industry data in this repository includes 2025 values. The linked global-share chart therefore caps its selected-year marker at 2023.
- MPOB PDF values that are not provided as machine-readable CSV are typed into `wrangle.py` with comments and mirrored in the small cleaned CSV files.

## Hand-drawn sketch

Add `sketch.pdf` before final submission. This file should be a real hand-drawn planning sketch that has been scanned or photographed and then linked/submitted through Moodle/GitHub; do not replace it with a digitally generated sketch.

## Run locally

Because Vega-Lite loads local CSV/JSON files, use a local web server instead of opening `index.html` directly from the filesystem.

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000/>.

## Regenerate data

```bash
python3 -m pip install -r requirements.txt
python3 wrangle.py
```

The cleaned files are committed in `data/` so the public page works without running Python.

## Repository structure

```text
index.html          Main single-page visualisation
css/style.css       Page layout and visual styling
charts/*.json       Vega-Lite chart/map specifications
data/*.csv          Cleaned small datasets used by Vega-Lite
raw/*               Original downloaded/source files used for reproducibility
wrangle.py          Script that regenerates cleaned datasets
requirements.txt    Python dependencies for wrangling
```

## Authorship

Created by Abdul Hakim Shaon, May 2026, for FIT2179 Data Visualisation 2 at Monash University Malaysia.
