# Adding a Certificate

This is the complete manual procedure for maintaining this repository. It is
deterministic: every step is a mechanical decision with a fixed answer. No AI
assistance, no interpretation, and no tooling beyond Python are required.

**The whole job is three steps.** Everything after the summary is reference
material for when you need to look something up.

---

## The three steps

1. **Copy the PDF** into the category folder that matches the certificate.
   Rename it to `YYYY-MM_issuer_short-title.pdf`.
2. **Add one row** to `metadata/certificates.csv` — ten fields, in order.
3. **Run the generator**, then commit and push:

   ```
   python scripts/generate_readme.py
   ```

That is the entire workflow. The sections below explain each step precisely.

---

## 1. Naming the file

```
YYYY-MM_issuer_short-title.pdf
```

- All lowercase.
- Words inside each part are separated by **hyphens**.
- **Underscores** appear exactly twice, separating the three parts.
- No spaces, no accents, no punctuation other than hyphens and the two
  underscores.
- `YYYY-MM` is the month the certificate was issued.
- `issuer` is a short slug for the organization — reuse the slug already used by
  that issuer's other files (see the table below).
- `short-title` is a shortened, recognisable form of the course title. It does
  not have to be the full title; the full title goes in the CSV.

Examples that are already in the repository:

```
2025-11_esri_processing-sar-data-in-arcgis-notebooks.pdf
2024-08_nasa-arset_drought-monitoring-prediction-projection.pdf
2023-04_amcham_quality-control-course.pdf
```

### Issuer slugs in use

| Organization | Slug |
| --- | --- |
| Esri | `esri` |
| ESGRS | `esgrs` |
| NASA ARSET | `nasa-arset` |
| NARSS | `narss` |
| NRIAG | `nriag` |
| ITIDA | `itida` |
| ALX Africa | `alx` |
| AmCham Egypt | `amcham` |
| A Capital Holding | `a-capital-holding` |

For a new organization, invent a short lowercase slug and add it to this table.

---

## 2. Choosing the category folder

There are exactly six categories. Pick the **one** that best describes the
subject of the course, then put the PDF in the matching folder.

| Category (use this exact spelling in the CSV) | Folder | Use it when the course is about |
| --- | --- | --- |
| `SAR/InSAR` | `certificates/sar-insar/` | Radar imaging, interferometry, deformation or subsidence monitoring |
| `Remote Sensing` | `certificates/remote-sensing/` | Optical/thermal imagery, image processing, Earth observation science |
| `GIS & Spatial Analysis` | `certificates/gis-spatial-analysis/` | GIS software, cartography, spatial analysis, web GIS, BIM integration |
| `Programming & GeoAI` | `certificates/programming-geoai/` | Python, machine learning, deep learning, AI applied to geospatial data |
| `Surveying & Geodesy` | `certificates/surveying-geodesy/` | Field surveying, levelling, GNSS, geodetic measurement |
| `Professional & Other` | `certificates/professional-other/` | Anything else — entrepreneurship, quality, soft skills, management |

### Documents that are not certifications

An internship reference letter, employer testimonial or similar record is **not**
a certificate. Set `credential_type` to `internship_reference`, and put the file
in `experience/internships/` rather than under `certificates/`. It is listed in
its own "Professional experience" section of the README and is deliberately
excluded from the certificate count. Its `category` field is still required — use
it as a subject tag.

**Tie-breaking rules**, so the same certificate always lands in the same place:

- If it involves radar, it is `SAR/InSAR` — even if it also teaches Python.
- If it teaches machine learning or programming applied to imagery, it is
  `Programming & GeoAI` — not `Remote Sensing`.
- If it is primarily about a GIS product or map-making, it is
  `GIS & Spatial Analysis`.
- If none of the five subject categories clearly applies, use
  `Professional & Other`. Do not invent a seventh category — the generator will
  flag it and the certificate will land in an "Uncategorized" table.

The category in the CSV and the folder on disk **must** match. The generator
checks this and warns if they disagree.

---

## 3. Adding the CSV row

Open `metadata/certificates.csv` and append one line at the bottom, above or
below the existing rows — **order does not matter**, the generator sorts
everything newest-first automatically.

The ten fields, in this exact order:

| # | Field | Required | What to write |
| --- | --- | --- | --- |
| 1 | `date` | Yes | `YYYY-MM`, e.g. `2025-11`. Same month as the filename. |
| 2 | `issuer` | Yes | Organization name as it should be displayed, e.g. `NASA ARSET`. |
| 3 | `title` | Yes | The course title exactly as printed on the certificate. |
| 4 | `category` | Yes | One of the six, spelled exactly as in the table above. |
| 5 | `field` | Recommended | A short topic tag, e.g. `InSAR`, `Cartography`, `Deep Learning`. |
| 6 | `credential_type` | Yes | `verified` if the issuer hosts an online verification page, `pdf` if not. Use `internship_reference` for a document that is **not** a certification (see below). |
| 7 | `credential_url` | If `verified` | The full `https://` verification URL. Leave empty when type is `pdf`. |
| 8 | `pdf_path` | Yes | Repo-relative path with forward slashes, e.g. `certificates/sar-insar/2025-11_esri_....pdf`. For `internship_reference`, use `experience/internships/`. |
| 9 | `description` | Recommended | One factual sentence about what the course covered. |
| 10 | `skills` | Recommended | Skills separated by **semicolons**: `InSAR;Python;Mapping`. |

### Two formatting rules that matter

- **Commas.** If any value contains a comma, wrap that value in double quotes:
  `"Drought Monitoring, Prediction and Projection"`. This is why `skills` uses
  semicolons — so you never have to quote it.
- **Empty fields.** Leave them empty, but keep the comma. A row always has nine
  commas separating ten fields.

### Copy-paste template

```
date,issuer,title,category,field,credential_type,credential_url,pdf_path,description,skills
```

A verified example:

```
2025-11,Esri,Processing SAR Data in ArcGIS Notebooks,SAR/InSAR,SAR Processing,verified,https://www.esri.com/verify/EXAMPLE,certificates/sar-insar/2025-11_esri_processing-sar-data-in-arcgis-notebooks.pdf,Processing and analysis of SAR imagery inside ArcGIS Notebooks.,SAR;ArcGIS Notebooks;Python
```

A PDF-only example:

```
2023-08,NARSS,Fundamentals of Remote Sensing and GIS,Remote Sensing,RS & GIS Fundamentals,pdf,,certificates/remote-sensing/2023-08_narss_fundamentals-of-remote-sensing-and-gis.pdf,Core principles of remote sensing and geographic information systems.,Remote Sensing;GIS;Image Interpretation
```

Note the **two commas together** in the PDF-only example — that is the empty
`credential_url`.

---

## 4. Regenerating the README

Validate first if you want to check your row before touching the README:

```
python scripts/generate_readme.py --check
```

This reads the CSV, prints any problems, and writes nothing.

Then regenerate:

```
python scripts/generate_readme.py
```

The script:

- reads **only** `metadata/certificates.csv` — nothing is guessed from filenames;
- sorts every category newest-first (ties broken alphabetically, so the output
  is identical every time);
- rebuilds `README.md` in a fixed format;
- prints warnings and notes, and always exits 0.

`README.md` is generated output. **Never edit it by hand** — the next run
overwrites your changes.

Finally, commit and push:

```
git add . && git commit -m "Add <certificate name>" && git push
```

Pushing to `main` also triggers `.github/workflows/update-readme.yml`, which
runs the same script on GitHub and commits the README if it differs. So if you
forget to run the script locally, the Action fixes it for you — running it
yourself is just faster feedback.

---

## What the generator checks

Every problem is reported as a warning; the script never crashes and never
blocks a commit. A warning means "fix this row", not "the build failed".

| Check | Message you will see |
| --- | --- |
| Missing required field | `missing required field(s): ...` |
| Bad date format | `date '2025/11' is not in YYYY-MM format.` |
| Category not one of the six | `unknown category '...'; allowed: ...` |
| `credential_type` not `verified`/`pdf` | `credential_type '...' must be one of: verified, pdf` |
| `verified` with no URL | `credential_type is 'verified' but credential_url is empty.` |
| `pdf` that has a URL anyway | `credential_type is 'pdf' but a credential_url is present.` |
| URL that is not `https://` | `credential_url should be an https:// URL.` |
| Same `pdf_path` used twice | `duplicate pdf_path — already used on row N` |
| Same date + issuer + title twice | `duplicate certificate — same date/issuer/title as row N.` |
| File in the wrong category folder | `file sits in certificates/X but category 'Y' expects certificates/Z.` |
| Empty `field`, `description` or `skills` | `field is empty.` etc. |
| Changed or reordered CSV columns | `missing column(s): ...` / `columns are out of order` |

Separately, `note` lines list rows whose PDF has not been copied into the
repository yet. That is informational — the certificate still appears in the
README, just without a `[PDF]` link until the file is added.

---

## Privacy reminder

This repository is public. Keep filenames, titles, descriptions and URLs limited
to the course, the issuer, the date and a public verification link. Never put
personal identifiers, certificate serial numbers used for account recovery, or
private links in the CSV.

---

## Troubleshooting

**A certificate is missing from the README.** It has no row in the CSV. The CSV
is the source of truth — copying a PDF into a folder does nothing on its own.

**A certificate appears under "Uncategorized".** Its `category` is misspelled.
Copy the exact spelling from the category table above.

**No `[PDF]` link appears.** Either `pdf_path` is wrong, or the file has not been
copied in yet. The generator prints a `note` line naming the path it looked for.

**The row shifted the columns.** A value contains a comma and was not quoted.
Wrap it in double quotes.

**`python` is not recognised.** Install Python 3 from python.org and tick "Add
python.exe to PATH". You can also skip the local run entirely — push your change
and let the GitHub Action regenerate the README.
