# Gambella (Gambela Region, Ethiopia) — data for the toilet project

Built 2026-11-15/16. Every source value has a source, URL and year in its row; values marked `derived` are calculated by Claude; gaps are `NOT FOUND` / `NOT ACCESSED`.

## Data (`data/`)
| File | What |
|---|---|
| `gambella_flood_drought_events.csv` | 29 flood/drought events 1961–2025, one row per source, with evidence quotes |
| `gambella_flood_drought_yearly.csv`, `ethiopia_flood_drought_yearly.csv` | Yearly counts (Gambella from the event file; Ethiopia from EM-DAT) |
| `gambella_economy_sanitation.csv` | GDP (national), modelled regional GNI/HDI/GDP, poverty, DHS sanitation/water/hygiene 2000–2024, camp latrine figures, cholera |
| `gambella_safety_gbv.csv` | DHS violence module 2016/2024, camp latrine-safety surveys, peer-reviewed GBV prevalence in camps/Gambella town |
| `sanitation_violence_literature.csv` | Studies linking toilet type to sexual violence (effect sizes as printed) |
| `gambella_grid_terrain.csv`, `gambella_grid_hazard.csv`, `gambella_grid_merged.csv` | 1,002 cells (0.05°): elevation, slope, population, soil, rainfall/drought, flood |
| `gambella_woreda_terrain.csv`, `gambella_woreda_hazard.csv`, `gambella_elevation_bands.csv` | Woreda and elevation-band summaries |
| `gambella_refugee_camps.csv` | Camp locations and populations (UNHCR 2022) |
| `ethiopia_regions_panel.csv` | 11 regions × 6 DHS years: sanitation, diarrhoea, wealth + GDL GNI/HDI |
| `correlations_grid.csv`, `correlations_regions.csv`, `correlations_yearly.csv`, `population_exposure.csv` | Claude's correlation and exposure analysis |

## Maps (`maps/`)
`gambella_heatmap_panel.png` (main heat map), single-layer `map_*.png`, `scatter_elevation.png`, `correlation_matrix_grid.png`, `panel_sanitation_income_rain.png`.

## Known limits
- WorldPop misses most of the ~370,000 camp refugees; grid population = host population.
- Flood extent is a global model (JRC); groundwater depth not found.
- No official regional GDP for Gambella; regional income figures are modelled (GDL, Kummu).
- GBV figures differ by definition and recall period; DHS reports are known to undercount.
- 2026-11-16: fixed a 0.1° westward shift of population in `scripts/04_grid_terrain.py` (old file in `raw/derived/grid_terrain_before_popfix.csv`).
- Independent re-check done 2026-11-16: each data file has a `verified` column (yes / no / not_checked). Fixes: 2007 flood figures (Ethiopia-wide DFO numbers removed; IFRC Gambella = 20,000 affected, not 36,090), two literature values, DHS help-seeking denominators.

## Rebuild
`scripts/04_grid_terrain.py <root>`, `scripts/hz0*.py`, `scripts/fd0*.py`, `scripts/es*.py`, `scripts/gbv15_build.py`, then `scripts/an01_geo_analysis.py <root>` and `scripts/an02_panel_yearly.py <root>`.
