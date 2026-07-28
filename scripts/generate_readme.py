#!/usr/bin/env python3
"""Regenerate README.md from metadata/certificates.csv.

metadata/certificates.csv is the SINGLE SOURCE OF TRUTH. This script performs
no inference of any kind: every value in the README is copied literally from a
CSV column. Adding a certificate is a manual, deterministic edit -- see
docs/ADDING-A-CERTIFICATE.md.

Usage:
    python scripts/generate_readme.py            regenerate README.md
    python scripts/generate_readme.py --check    validate only, write nothing

Exit code is always 0 unless the CSV is missing or unreadable; validation
problems are reported as warnings so a bad row never blocks a push.
Standard library only. Runnable from any working directory.
"""

import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = REPO_ROOT / "metadata" / "certificates.csv"
README_PATH = REPO_ROOT / "README.md"
GUIDE_PATH = "docs/ADDING-A-CERTIFICATE.md"

NAME = "Ahmed Ibrahim"
ROLE = (
    "Geomatics graduate & M.Sc. candidate — SAR/InSAR Remote Sensing, "
    "Earth Observation & GIS"
)
LINKEDIN = "https://linkedin.com/in/ahmedibrahimid"

# The exact CSV header, in order. A mismatch is reported as a warning.
FIELDS = [
    "date",
    "issuer",
    "title",
    "category",
    "field",
    "credential_type",
    "credential_url",
    "pdf_path",
    "description",
    "skills",
]

# Fields that must be non-empty on every row.
REQUIRED = ["date", "issuer", "title", "category", "credential_type", "pdf_path"]

# Category -> folder slug under certificates/. Fixed display order.
CATEGORIES = {
    "SAR/InSAR": "sar-insar",
    "Remote Sensing": "remote-sensing",
    "GIS & Spatial Analysis": "gis-spatial-analysis",
    "Programming & GeoAI": "programming-geoai",
    "Surveying & Geodesy": "surveying-geodesy",
    "Professional & Other": "professional-other",
}
CATEGORY_ORDER = list(CATEGORIES)

CREDENTIAL_TYPES = ["verified", "pdf", "internship_reference"]

# Types that are NOT certifications. They are listed separately, excluded from
# the certificate counts, and live outside certificates/.
NON_CERTIFICATE_TYPES = {"internship_reference"}

# Where a non-certificate document is expected to sit, by credential_type.
NON_CERTIFICATE_FOLDERS = {"internship_reference": "experience/internships"}

SKILL_SEPARATOR = ";"

warnings = []
notices = []


def warn(row_number, message):
    warnings.append(message)
    print("WARNING  row %s: %s" % (row_number, message))


def notice(message):
    notices.append(message)
    print("note     %s" % message)


def read_rows():
    """Return (rows, header). Blank lines and #-comments are skipped."""
    if not CSV_PATH.is_file():
        print("ERROR: %s not found." % CSV_PATH)
        sys.exit(1)

    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as fh:
        lines = [
            line for line in fh if line.strip() and not line.lstrip().startswith("#")
        ]

    if not lines:
        print("ERROR: %s contains no header row." % CSV_PATH)
        sys.exit(1)

    reader = csv.DictReader(lines)
    header = reader.fieldnames or []
    rows = []
    for index, raw in enumerate(reader, start=2):
        row = {f: (raw.get(f) or "").strip() for f in FIELDS}
        row["_line"] = index
        rows.append(row)
    return rows, header


def validate(rows, header):
    """Report every problem found. Returns the rows that can be rendered."""
    if header != FIELDS:
        missing = [f for f in FIELDS if f not in header]
        extra = [f for f in header if f not in FIELDS]
        if missing:
            warn("header", "missing column(s): %s" % ", ".join(missing))
        if extra:
            warn("header", "unexpected column(s): %s" % ", ".join(extra))
        if not missing and not extra:
            warn("header", "columns are out of order; expected: %s" % ", ".join(FIELDS))

    seen_paths = {}
    seen_identity = {}
    usable = []

    for row in rows:
        line = row["_line"]
        label = row["title"] or row["pdf_path"] or "(untitled)"

        empty = [f for f in REQUIRED if not row[f]]
        if empty:
            warn(line, "%s — missing required field(s): %s" % (label, ", ".join(empty)))

        if row["date"] and not is_year_month(row["date"]):
            warn(line, "%s — date %r is not in YYYY-MM format." % (label, row["date"]))

        if row["category"] and row["category"] not in CATEGORIES:
            warn(
                line,
                "%s — unknown category %r; allowed: %s"
                % (label, row["category"], " | ".join(CATEGORY_ORDER)),
            )

        ctype = row["credential_type"].lower()
        if ctype and ctype not in CREDENTIAL_TYPES:
            warn(
                line,
                "%s — credential_type %r must be one of: %s"
                % (label, row["credential_type"], ", ".join(CREDENTIAL_TYPES)),
            )
        elif ctype == "verified" and not row["credential_url"]:
            warn(line, "%s — credential_type is 'verified' but credential_url is empty." % label)
        elif ctype != "verified" and row["credential_url"]:
            warn(
                line,
                "%s — credential_type is %r but a credential_url is present."
                % (label, row["credential_type"]),
            )

        if row["credential_url"] and not row["credential_url"].startswith("https://"):
            warn(line, "%s — credential_url should be an https:// URL." % label)

        if not row["field"]:
            warn(line, "%s — field is empty." % label)
        if not row["description"]:
            warn(line, "%s — description is empty." % label)
        if not row["skills"]:
            warn(line, "%s — skills is empty." % label)

        # Duplicate detection.
        path_key = row["pdf_path"].lower()
        if path_key:
            if path_key in seen_paths:
                warn(line, "duplicate pdf_path — already used on row %d: %s" % (seen_paths[path_key], row["pdf_path"]))
            else:
                seen_paths[path_key] = line

        identity = (row["date"].lower(), row["issuer"].lower(), row["title"].lower())
        if all(identity):
            if identity in seen_identity:
                warn(line, "duplicate certificate — same date/issuer/title as row %d." % seen_identity[identity])
            else:
                seen_identity[identity] = line

        # The PDF file itself is optional until it is copied in; not a warning.
        if row["pdf_path"]:
            if not (REPO_ROOT / row["pdf_path"]).is_file():
                notice("PDF not yet in the repository: %s" % row["pdf_path"])
            elif ctype in NON_CERTIFICATE_TYPES:
                expected = NON_CERTIFICATE_FOLDERS[ctype]
                actual = Path(row["pdf_path"]).parent.as_posix()
                if actual != expected:
                    warn(
                        line,
                        "%s — credential_type %r expects the file in %s/ but it sits in %s/."
                        % (label, ctype, expected, actual),
                    )
            else:
                expected = CATEGORIES.get(row["category"])
                folder = Path(row["pdf_path"]).parent.name
                if expected and folder != expected:
                    warn(
                        line,
                        "%s — file sits in certificates/%s but category %r expects certificates/%s."
                        % (label, folder, row["category"], expected),
                    )

        if row["title"]:
            usable.append(row)
        else:
            warn(line, "row skipped — a title is required to render it.")

    return usable


def is_year_month(value):
    parts = value.split("-")
    if len(parts) != 2:
        return False
    year, month = parts
    if not (year.isdigit() and len(year) == 4):
        return False
    if not (month.isdigit() and len(month) == 2):
        return False
    return 1 <= int(month) <= 12


def escape(text):
    return text.replace("|", "\\|")


def credential_cell(row):
    parts = []
    if row["credential_url"]:
        parts.append("🔗 [Verify](%s)" % row["credential_url"])
    if row["pdf_path"] and (REPO_ROOT / row["pdf_path"]).is_file():
        parts.append("[PDF](%s)" % row["pdf_path"])
    return " · ".join(parts) if parts else "—"


def certificate_cell(row):
    text = "**%s**" % escape(row["title"])
    if row["description"]:
        text += "<br>%s" % escape(row["description"])
    return text


def skills_cell(row):
    if not row["skills"]:
        return "—"
    skills = [s.strip() for s in row["skills"].split(SKILL_SEPARATOR) if s.strip()]
    return escape(" · ".join(skills))


def sort_key(row):
    """Newest first; ties broken alphabetically for a stable, repeatable order."""
    return (row["date"], row["title"].lower())


def build_readme(all_rows):
    # Non-certificate documents (internship references and the like) are listed
    # separately and never counted as certifications.
    rows = [r for r in all_rows if r["credential_type"].lower() not in NON_CERTIFICATE_TYPES]
    other = [r for r in all_rows if r["credential_type"].lower() in NON_CERTIFICATE_TYPES]

    total = len(rows)
    issuers = {r["issuer"] for r in rows if r["issuer"]}
    verified = [r for r in rows if r["credential_type"].lower() == "verified"]

    out = []
    add = out.append

    add("# Professional Certificates")
    add("")
    add("**%s** — %s" % (NAME, ROLE))
    add("")
    add("[LinkedIn](%s)" % LINKEDIN)
    add("")
    add(
        "An index of my professional training in remote sensing, SAR/InSAR, GIS "
        "and Earth observation. Certificates marked 🔗 can be verified directly "
        "with the issuing organization; the remainder are held here as PDFs."
    )
    add("")
    add(
        "> This file is generated from `metadata/certificates.csv` by "
        "`scripts/generate_readme.py`. Do not hand-edit it — see "
        "[Maintaining this index](#maintaining-this-index)."
    )
    add("")
    add(
        "**%d certificate%s** across **%d issuer%s** — **%d** with an online "
        "verification link, **%d** PDF only."
        % (
            total,
            "" if total == 1 else "s",
            len(issuers),
            "" if len(issuers) == 1 else "s",
            len(verified),
            total - len(verified),
        )
    )
    add("")

    listed = set()
    for category in CATEGORY_ORDER:
        entries = [r for r in rows if r["category"] == category]
        listed.update(id(r) for r in entries)
        if not entries:
            continue
        add("### %s" % category)
        add("")
        add("| Date | Certificate | Issuer | Field | Skills | Credential |")
        add("| --- | --- | --- | --- | --- | --- |")
        for row in sorted(entries, key=sort_key, reverse=True):
            add(
                "| %s | %s | %s | %s | %s | %s |"
                % (
                    escape(row["date"]),
                    certificate_cell(row),
                    escape(row["issuer"]),
                    escape(row["field"]) if row["field"] else "—",
                    skills_cell(row),
                    credential_cell(row),
                )
            )
        add("")

    # Rows whose category is not in the fixed list would otherwise vanish.
    orphans = [r for r in rows if id(r) not in listed]
    if orphans:
        add("### Uncategorized")
        add("")
        add(
            "These rows carry a category outside the allowed list and need to be "
            "corrected in `metadata/certificates.csv`."
        )
        add("")
        add("| Date | Certificate | Issuer | Category as written | Credential |")
        add("| --- | --- | --- | --- | --- |")
        for row in sorted(orphans, key=sort_key, reverse=True):
            add(
                "| %s | %s | %s | %s | %s |"
                % (
                    escape(row["date"]),
                    certificate_cell(row),
                    escape(row["issuer"]),
                    escape(row["category"]) if row["category"] else "—",
                    credential_cell(row),
                )
            )
        add("")

    if other:
        add("## Professional experience")
        add("")
        add(
            "Supporting documents that are **not** certifications — internship "
            "reference letters and similar records. They are listed here for "
            "completeness and are excluded from the certificate count above."
        )
        add("")
        add("| Date | Document | Issuer | Field | Skills | Type |")
        add("| --- | --- | --- | --- | --- | --- |")
        for row in sorted(other, key=sort_key, reverse=True):
            label = row["credential_type"].replace("_", " ").capitalize()
            link = (
                "[%s](%s)" % (label, row["pdf_path"])
                if row["pdf_path"] and (REPO_ROOT / row["pdf_path"]).is_file()
                else escape(label)
            )
            add(
                "| %s | %s | %s | %s | %s | %s |"
                % (
                    escape(row["date"]),
                    certificate_cell(row),
                    escape(row["issuer"]),
                    escape(row["field"]) if row["field"] else "—",
                    skills_cell(row),
                    link,
                )
            )
        add("")

    add("## Maintaining this index")
    add("")
    add(
        "`metadata/certificates.csv` is the single source of truth. Adding a "
        "certificate is a manual, three-step process — no tooling beyond Python "
        "and no interpretation required:"
    )
    add("")
    add("1. Copy the PDF into the category folder that matches the certificate.")
    add("2. Add one row to `metadata/certificates.csv`.")
    add("3. Run `python scripts/generate_readme.py` and commit.")
    add("")
    add(
        "The full procedure — the filename convention, how to pick a category, "
        "and what every column means — is in "
        "[%s](%s). Run `python scripts/generate_readme.py --check` at any time "
        "to validate the CSV without rewriting this file." % (GUIDE_PATH, GUIDE_PATH)
    )
    add("")
    add("Category folders under `certificates/`:")
    add("")
    add("| Category | Folder |")
    add("| --- | --- |")
    for category in CATEGORY_ORDER:
        add("| %s | `certificates/%s/` |" % (escape(category), CATEGORIES[category]))
    add("")
    add(
        "This repository is public. Keep filenames and CSV rows limited to the "
        "course, issuer, date and a public verification URL — no personal "
        "identifiers, no private links."
    )
    add("")
    add("## Note on reuse")
    add("")
    add(
        "The certificates in this repository are my personal credentials. They "
        "are published for verification purposes only and are not offered for "
        "reuse, redistribution or modification."
    )
    add("")

    return "\n".join(out)


def main(argv):
    check_only = "--check" in argv[1:]

    rows, header = read_rows()
    usable = validate(rows, header)
    readme = build_readme(usable)

    if check_only:
        print("")
        print(
            "Checked %d row(s): %d warning(s), %d note(s). Nothing written (--check)."
            % (len(rows), len(warnings), len(notices))
        )
        return 0

    with README_PATH.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(readme)

    print("")
    print(
        "Wrote README.md from %d row(s): %d listed, %d warning(s), %d note(s)."
        % (len(rows), len(usable), len(warnings), len(notices))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
