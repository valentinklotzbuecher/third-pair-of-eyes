# Intake — <product title> (<internal ID>, <revision>)

Suite version: <copy metadata.version from the stats-review SKILL.md>
Intake date: <yyyy-mm-dd>

## Settings

- Product type: <sse | protocol | sap | report | manuscript | other> (profile: references/product-profiles.md)
- Data mode: <none | synthetic | shared> — <what it permits, one line>
- Depth: <quick | standard | full>
- Clearance: <the assignment's Documents and Data clearance lines, verbatim>

## Documents

| Document | Path | Title | Version / revision | Date | Status |
|---|---|---|---|---|---|
| Product (rendered) | 01_product/<file> | | | | |
| Product (source) | 01_product/<file> | | | | |

Governing documents not in the job (and so `unverified-here` for every check that needs them): <list, or "none">.

## DKF product fields

<from review/intake-scan.json: internal ID, product type, level of assumptions, influence on protocol, multicentre, risk; "not present" when the source has no dkfreporting params>

## Render environment

<R and package versions the rendered PDF records; groundhog date or renv.lock; differences found>

## Questions from the assignment

Q1. <verbatim>
Q2. <verbatim>

## Inventory

<files by folder, from review/intake-scan.json: path, size, class; data-like files and their clearance>

## Requests for the operator

<stage agents cannot ask the operator directly; each request goes here with the date and the stage that needs it, and the run continues by rule. "None" when empty.>
