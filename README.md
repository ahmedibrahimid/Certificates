# Professional Certificates

**Ahmed Ibrahim** — Geomatics Engineer & M.Sc. candidate — SAR/InSAR Remote Sensing, Earth Observation & GIS

[LinkedIn](https://linkedin.com/in/ahmedibrahimid)

A verified index of my professional training in remote sensing, SAR/InSAR, GIS and Earth observation. Each entry links to the certificate itself and, where the issuer provides one, to a public verification page.

> The tables below are generated from the certificate files in this repository. Do not hand-edit them — see [How to add a new certificate](#how-to-add-a-new-certificate).

**5 certificates** across **3 issuers.**

### SAR/InSAR

| Date | Certificate | Issuer | Links |
| --- | --- | --- | --- |
| 2025-11 | Processing SAR Data with ArcGIS Notebooks | Esri | [PDF](certificates/esri/2025-11_esri_processing-sar-data-arcgis-notebooks.pdf) |

### Remote Sensing

| Date | Certificate | Issuer | Links |
| --- | --- | --- | --- |
| 2025-11 | Imagery in Action (ArcGIS MOOC) | Esri | [PDF](certificates/esri/2025-11_esri_arcgis-imagery-mooc.pdf) |
| 2024-08 | Drought Monitoring and Prediction Using Earth Observations | NASA ARSET | [PDF](certificates/nasa-arset/2024-08_nasa-arset_drought-monitoring.pdf) |
| 2024-02 | Advanced Remote Sensing with ENVI | NARSS | [PDF](certificates/narss/2024-02_narss_advanced-remote-sensing-envi.pdf) |

### GIS & Spatial Analysis

| Date | Certificate | Issuer | Links |
| --- | --- | --- | --- |
| 2023-10 | Spatial Data Science: The New Frontier in Analytics | Esri | [PDF](certificates/esri/2023-10_esri_spatial-data-science.pdf) |

## How to add a new certificate

1. Name the file using the convention:

   ```
   YYYY-MM_issuer_short-course-title.pdf
   ```

   Lowercase, hyphen-separated words, and underscores only as the three top-level separators (date, issuer, title). For example: `2025-11_esri_processing-sar-data-arcgis-notebooks.pdf`.
2. Drop it into the matching issuer folder under `certificates/` (use `certificates/other/` if the issuer has no folder yet).
3. Optionally add a row to `metadata/certificates.csv` to attach a verification link, set the category, or give the exact course wording. Rows are keyed by `file_path`; empty fields keep the value derived from the filename.
4. Commit and push. The GitHub Action regenerates this README automatically — running `python scripts/generate_readme.py` locally is only needed to preview the result.

This repository is public, so keep filenames and CSV rows limited to the course, issuer, date and a public verification URL — no personal identifiers or private links.

## Note on reuse

The certificates in this repository are my personal credentials. They are published for verification purposes only and are not offered for reuse, redistribution or modification.
