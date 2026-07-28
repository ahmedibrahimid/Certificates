#!/usr/bin/env python3
"""Generate README.md from the certificate files on disk.

The files under certificates/ are the source of truth: dropping a correctly
named PDF into the tree is enough to make it appear in the README.
metadata/certificates.csv is an optional enrichment layer that can override
individual fields and assign categories.

Filename convention:  YYYY-MM_issuer_short-course-title.pdf

Standard library only. Safe to run from any working directory.
"""

import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CERTS_DIR = REPO_ROOT / "certificates"
CSV_PATH = REPO_ROOT / "metadata" / "certificates.csv"
README_PATH = REPO_ROOT / "README.md"

NAME = "Ahmed Ibrahim"
ROLE = (
    "Geomatics graduate & M.Sc. candidate — SAR/InSAR Remote Sensing, "
    "Earth Observation & GIS"
)
LINKEDIN = "https://linkedin.com/in/ahmedibrahimid"

# Known issuer slugs -> canonical display names. Unknown slugs are title-cased.
ISSUERS = {
    "esri": "Esri",
    "nasa-arset": "NASA ARSET",
    "narss": "NARSS",
    "nriag": "NRIAG",
    "mbrsc": "MBRSC",
    "amcham": "AmCham Egypt",
    "alx": "ALX",
    "itida": "ITIDA/TIEC",
}

# Words that should not be plain title-cased when derived from a filename slug.
ACRONYMS = {
    "sar": "SAR",
    "insar": "InSAR",
    "gis": "GIS",
    "gnss": "GNSS",
    "gps": "GPS",
    "dem": "DEM",
    "dsm": "DSM",
    "sql": "SQL",
    "api": "API",
    "ai": "AI",
    "ml": "ML",
    "geoai": "GeoAI",
    "uav": "UAV",
    "lidar": "LiDAR",
    "arcgis": "ArcGIS",
    "qgis": "QGIS",
    "envi": "ENVI",
    "snap": "SNAP",
    "nasa": "NASA",
    "esa": "ESA",
    "usgs": "USGS",
    "modis": "MODIS",
    "ndvi": "NDVI",
    "3d": "3D",
    "2d": "2D",
    "eo": "EO",
    "mooc": "MOOC",
}

CATEGORY_ORDER = [
    "SAR/InSAR",
    "Remote Sensing",
    "GIS & Spatial Analysis",
    "Programming & GeoAI",
    "Surveying & Geodesy",
    "Professional & Other",
]
DEFAULT_CATEGORY = "Professional & Other"

CSV_FIELDS = ["date", "issuer", "title", "category", "credential_url", "file_path"]

warnings = []


def warn(message):
    warnings.append(message)
    print("warning: " + message)


def humanize(slug):
    """Turn a hyphenated slug into readable title-cased text."""
    words = [w for w in slug.split("-") if w]
    out = []
    for word in words:
        out.append(ACRONYMS.get(word.lower(), word.capitalize()))
    return " ".join(out)


def issuer_name(slug):
    return ISSUERS.get(slug.lower(), humanize(slug))


def rel_path(path):
    """Repo-relative path with forward slashes (used as the CSV key)."""
    return path.relative_to(REPO_ROOT).as_posix()


def parse_filename(path):
    """Derive date / issuer / title from a certificate filename."""
    parts = path.stem.split("_")
    folder_slug = path.parent.name

    date = parts[0] if len(parts) >= 1 else ""
    if len(parts) >= 3:
        issuer_slug = parts[1]
        title_slug = "_".join(parts[2:])
    elif len(parts) == 2:
        # Ambiguous: no distinct issuer field, fall back to the parent folder.
        issuer_slug = folder_slug
        title_slug = parts[1]
    else:
        issuer_slug = folder_slug
        title_slug = path.stem

    if not issuer_slug or issuer_slug == "certificates":
        issuer_slug = folder_slug

    return {
        "date": date,
        "issuer": issuer_name(issuer_slug),
        "title": humanize(title_slug.replace("_", "-")),
        "category": DEFAULT_CATEGORY,
        "credential_url": "",
        "file_path": rel_path(path),
    }


def discover():
    if not CERTS_DIR.is_dir():
        warn("certificates/ directory not found — no certificates discovered.")
        return []
    files = sorted(CERTS_DIR.rglob("*.pdf"), key=lambda p: rel_path(p))
    return [parse_filename(p) for p in files]


def load_overrides():
    """Read the optional CSV enrichment layer, keyed by file_path."""
    overrides = {}
    if not CSV_PATH.is_file():
        return overrides

    with CSV_PATH.open("r", encoding="utf-8", newline="") as fh:
        rows = [
            line
            for line in fh
            if line.strip() and not line.lstrip().startswith("#")
        ]

    if not rows:
        return overrides

    for row in csv.DictReader(rows):
        key = (row.get("file_path") or "").strip().replace("\\", "/")
        if not key:
            warn("CSV row without a file_path was ignored.")
            continue
        cleaned = {}
        for field in CSV_FIELDS:
            value = (row.get(field) or "").strip()
            if value:
                cleaned[field] = value
        category = cleaned.get("category")
        if category and category not in CATEGORY_ORDER:
            warn(
                "unknown category %r for %s — falling back to %r."
                % (category, key, DEFAULT_CATEGORY)
            )
            cleaned.pop("category")
        overrides[key] = cleaned
    return overrides


def merge(certificates, overrides):
    known = {c["file_path"] for c in certificates}
    for key in sorted(overrides):
        if key not in known:
            warn("CSV row points at a missing file: %s" % key)

    for cert in certificates:
        for field, value in overrides.get(cert["file_path"], {}).items():
            if field == "file_path":
                continue
            cert[field] = value
    return certificates


def escape(text):
    return text.replace("|", "\\|")


def links_cell(cert):
    parts = []
    if cert["file_path"]:
        parts.append("[PDF](%s)" % cert["file_path"])
    if cert["credential_url"]:
        parts.append("[Verify](%s)" % cert["credential_url"])
    return " · ".join(parts) if parts else "—"


def build_readme(certificates):
    total = len(certificates)
    issuers = {c["issuer"] for c in certificates}

    lines = []
    lines.append("# Professional Certificates")
    lines.append("")
    lines.append("**%s** — %s" % (NAME, ROLE))
    lines.append("")
    lines.append("[LinkedIn](%s)" % LINKEDIN)
    lines.append("")
    lines.append(
        "A verified index of my professional training in remote sensing, "
        "SAR/InSAR, GIS and Earth observation. Each entry links to the "
        "certificate itself and, where the issuer provides one, to a public "
        "verification page."
    )
    lines.append("")
    lines.append(
        "> The tables below are generated from the certificate files in this "
        "repository. Do not hand-edit them — see "
        "[How to add a new certificate](#how-to-add-a-new-certificate)."
    )
    lines.append("")
    lines.append(
        "**%d certificate%s** across **%d issuer%s.**"
        % (total, "" if total == 1 else "s", len(issuers), "" if len(issuers) == 1 else "s")
    )
    lines.append("")

    for category in CATEGORY_ORDER:
        entries = [c for c in certificates if c["category"] == category]
        if not entries:
            continue
        entries.sort(key=lambda c: (c["date"], c["title"]), reverse=True)
        lines.append("### %s" % category)
        lines.append("")
        lines.append("| Date | Certificate | Issuer | Links |")
        lines.append("| --- | --- | --- | --- |")
        for cert in entries:
            lines.append(
                "| %s | %s | %s | %s |"
                % (
                    escape(cert["date"]),
                    escape(cert["title"]),
                    escape(cert["issuer"]),
                    links_cell(cert),
                )
            )
        lines.append("")

    lines.append("## How to add a new certificate")
    lines.append("")
    lines.append("1. Name the file using the convention:")
    lines.append("")
    lines.append("   ```")
    lines.append("   YYYY-MM_issuer_short-course-title.pdf")
    lines.append("   ```")
    lines.append("")
    lines.append(
        "   Lowercase, hyphen-separated words, and underscores only as the "
        "three top-level separators (date, issuer, title). For example: "
        "`2025-11_esri_processing-sar-data-arcgis-notebooks.pdf`."
    )
    lines.append(
        "2. Drop it into the matching issuer folder under `certificates/` "
        "(use `certificates/other/` if the issuer has no folder yet)."
    )
    lines.append(
        "3. Optionally add a row to `metadata/certificates.csv` to attach a "
        "verification link, set the category, or give the exact course "
        "wording. Rows are keyed by `file_path`; empty fields keep the value "
        "derived from the filename."
    )
    lines.append(
        "4. Commit and push. The GitHub Action regenerates this README "
        "automatically — running `python scripts/generate_readme.py` locally "
        "is only needed to preview the result."
    )
    lines.append("")
    lines.append(
        "This repository is public, so keep filenames and CSV rows limited to "
        "the course, issuer, date and a public verification URL — no personal "
        "identifiers or private links."
    )
    lines.append("")
    lines.append("## Note on reuse")
    lines.append("")
    lines.append(
        "The certificates in this repository are my personal credentials. "
        "They are published for verification purposes only and are not "
        "offered for reuse, redistribution or modification."
    )
    lines.append("")

    return "\n".join(lines)


def main():
    certificates = merge(discover(), load_overrides())
    readme = build_readme(certificates)

    with README_PATH.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(readme)

    print(
        "Wrote %s — %d certificate(s), %d warning(s)."
        % (rel_path(README_PATH), len(certificates), len(warnings))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
