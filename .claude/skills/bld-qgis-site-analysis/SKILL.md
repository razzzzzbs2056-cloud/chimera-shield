---
name: bld-qgis-site-analysis
description: Site and hazard analysis in QGIS (PyQGIS or qgis_process): terrain, slope, flood, geology, faults, liquefaction and landslide layers, utilities, access, solar exposure; produces a constraints map and a missing-data list. Use as soon as a site location exists.
---

# QGIS site analysis

**Status here:** not installed; the project has no site yet. Layer plan: `architecture/reports/engineering-report-v0.1.md` §4.

## Workflow
1. Project CRS: the national projected CRS for the site (metres). Never measure in geographic degrees.
2. Load authoritative layers first: cadastre/planning (local government), DEM (national mapping agency; Copernicus DEM as fallback), flood maps, geology and fault maps (national geological survey), seismic hazard (national model), utilities (owners). OpenStreetMap only as indicative context.
3. Processing (headless): `qgis_process run native:slope`, `native:hillshade`, `gdal:contour`, buffers around faults and watercourses, `native:intersection` for constraint overlap, zonal statistics for flood depth.
4. Solar/wind: climate files for the nearest station; horizon/shadow analysis from the DEM and neighbour heights.
5. Outputs to `architecture/gis/`: the `.qgz` project, GeoPackage layers, a constraints map, and a table of findings with evidence tags and data dates.

## Verify
Data source, date and licence recorded for every layer · CRS consistent · spot-check against survey points · flag where resolution is too coarse for the decision.

## Limits
GIS data is not a project survey or a geotechnical investigation. Hazard layers inform scope; they do not set design values unless they are the code's official maps.
