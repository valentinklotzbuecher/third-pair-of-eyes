# Data access and data protection

Everything the agent reads is sent to the model provider. What may be read is therefore
a decision the operator makes before the run and records in `00_ASSIGNMENT.md`; the
review enforces it and never widens it. When in doubt, the review reads less and
records the limit.

At the time of writing the DKF has no zero-data-retention agreement with a model
provider, so assume that everything sent is retained under the provider's standard
terms. Check the current DKF rules before clearing anything beyond the default.

## What needs clearance

| Material | Typical status | Clearance |
|---|---|---|
| Methods text and statistical code (SSE, SAP, protocol statistics sections, analysis code) | usually cleared under the DKF rules for LLM use | the operator confirms in `Documents:` |
| Protocol drafts and other sponsor documents | may be confidential to the sponsor or PI | the operator confirms, naming the document |
| Reports and manuscripts with results of an unpublished study | aggregate but confidential results | the operator confirms, naming who agreed (PI, sponsor) |
| Patient-level data, coded or not | never by default | data mode `shared` only, with `Data clearance:` naming who approved it and on what basis |
| Synthetic or dummy data, codebooks built under the disclosure rules below | cleared once the statistician has checked them | data mode `synthetic` |

## Data modes

- **`none`** (default). The review reads documents and code, and runs code that needs
  no patient data: sample size calculations, simulations, arithmetic on printed
  numbers. Chunks that read patient data are not run.
- **`synthetic`**. In addition, the review runs the code on dummy data with the
  structure the code expects. Three routes, in order of preference:
  1. *Schema only*: `stats-synthetic-data` infers the data contract from the code and the
     documents (variable names, types, levels, units, visit structure) and generates
     data from it. No real data are touched at any point.
  2. *Codebook*: the statistician runs `make_codebook.R` (in the `stats-synthetic-data`
     skill's `assets/`) locally on the real data. It writes a codebook under the
     disclosure rules below; the statistician reads it, removes anything they would
     not hand to a colleague outside the study, and puts it in `05_synthetic/`. The
     agent generates data from the codebook.
  3. *Provided*: the statistician supplies dummy data they made themselves, for
     example test records from the data-management system or the dummy data a SAP was
     programmed on, in `05_synthetic/`.
- **`shared`**. The review reads patient-level data in `04_data/`. Only with a
  `Data clearance:` line in the assignment naming who approved the use and on what
  basis (consent and ethics approval covering processing by this provider, a data
  transfer or processing agreement, or data that are anonymous in the legal sense).
  The review cannot verify a clearance; it records it.

## The guard

`scripts/scan_job.py` runs before anything is opened. It lists every file with its
size and hash, classifies data-like files by extension and location (`.csv`, `.rds`,
`.rda`, `.RData`, `.sav`, `.dta`, `.sas7bdat`, `.xpt`, `.xlsx`, `.parquet`, `.feather`,
`.json` outside the review's own folders), and fails when such a file sits where the
data mode does not allow it:

- mode `none`: data-like files are allowed only inside `01_product/` and only when the
  assignment lists them as non-patient files (saved simulation results, lookup tables,
  planning inputs) under `Non-patient files:`;
- mode `synthetic`: also `05_synthetic/`;
- mode `shared`: also `04_data/`.

A failing scan stops the run before any file is read. The agent records the names and
sizes only and asks the operator. It never opens a file "to check whether it is real
data".

## Disclosure rules for everything the review writes

These hold in every mode, `shared` included, because review artifacts travel further
than the data.

- Aggregates only. No row-level values in logs, reports or messages: no `head()`,
  `print(df)`, `str()` on patient data, `View()`, or error messages that echo rows.
  Log `nrow`, counts, means and model summaries instead.
- No identifiers, dates of birth, exact event dates or free text from patient data.
- No cell below 5 that the delivered product does not already print; show `<5`.
- Codebooks from `make_codebook.R`: variable names, types, labels, factor levels (with
  levels holding fewer than 5 records merged or listed without counts), numeric ranges
  rounded outward to a coarse grid, missingness proportions rounded to 5 percentage
  points, date ranges at month resolution, no free-text values. The statistician reads
  it before handing it over.
- Web searches and other external tools get general terms (condition, intervention,
  endpoint, design), never internal IDs, unpublished results or data.

## What each mode can establish, and how to say so

| Situation | Status | Standard wording |
|---|---|---|
| Printed number depends on patient data, mode `none` | `unverified-here` | "Not reproduced here: patient data were not shared for this review. The table's arithmetic and internal consistency were checked." |
| Code ran on synthetic data | evidence about code behaviour | "The code runs on synthetic data with the documented structure and implements the stated specification; this does not check the printed numbers." |
| Code fails on synthetic data with values the data contract allows | finding | state the value class and the failure |
| Mode `shared`, number reproduced | (no sentence: success is the baseline) | — |
| Mode `shared`, number not reproduced | finding | the printed value, the reproduced value, the difference, the repair log |
| A saved result loaded by the document, no code in the job made it | `unverifiable as delivered` (a finding) | "The saved simulation result is loaded but not produced by the delivered code." |

A limit is reported once per result family, in the synthesis's limits section, never
as a fault of the product.
