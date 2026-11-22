# Assignment

<!-- Written by the statistician who asks for the review (the operator). The review reads
     this file first and never widens what it clears. Lines starting with "- Field:" are
     read by scan_job.py: keep the field names. Delete these comments if you like. -->

## Product

- Statistical product: <file name of the rendered product, e.g. th26Example2SSE001.pdf>
- Product type: <sse | protocol | sap | report | manuscript | other>
- Title: <study title or product title>
- Internal ID: <internal ID, if any>
- Version: <revision, date or version line as printed>
- Author(s): <statistician(s)>
- Human reviewer: <colleague who will do the consistency review>

## Important issues for reviewer

<!-- The questions you want answered, one per item, as you would write them in the
     consistency review's Assignment section. They are answered one by one. -->

1. <question>
2. <question>

## Other documents this product depends on

<!-- Each with its path in the job folder. Missing documents: say so. -->

- Study protocol: 02_governing/<file>
- Saved results the product loads: 01_product/<path>
- Cited sources for planning values: lit/

## Clearance

<!-- What may be sent to the model provider. See the stats-review skill,
     references/data-access.md. Patient-level data is never sent unless the data mode
     is `shared` and the data clearance names who approved it and on what basis. -->

- Documents: <what is cleared and by whom, e.g. "SSE text and code, protocol draft v1.2: no patient data; cleared under the institution's rules for LLM use (VK, 2026-10-27)">
- Data mode: <none | synthetic | shared>
- Non-patient files: <data-like files inside 01_product/ that hold no patient data, e.g. dat/calc.rds (saved simulation results); or "none">
- Data clearance: <only for mode `shared`: who approved processing of which data by which provider, on what basis; otherwise "not applicable">

## Review settings

- Depth: <quick | standard | full>
- Focus: <optional: sections or questions to prioritise; anything out of scope>
