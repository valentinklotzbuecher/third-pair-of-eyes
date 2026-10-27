# Source acquisition and verification

For every source a statement rests on: the governing documents, and the works cited
for planning values, effect sizes and methods. Adapted from the upstream protocol.

## Bounded acquisition

0. **The job folder first**: `02_governing/`, `lit/`, and anything the product's source
   tree carries (a `.bib` file, a folder of references). A source recorded as
   unobtainable while a copy sits in the job is a self-inflicted gap.
1. The citation as printed: DOI, PubMed ID, registry number.
2. Open-access copies: PubMed Central, the publisher's open-access version, preprint
   servers, the trial registry's results section.
3. Exact-title search with authors, year and journal; then variant titles.
4. The operator's library access (the university library, interlibrary loan).
   Unattended, log the request the operator must make, record the source
   `BLOCKED — operator access`, and continue; rows resting on it stay `INTERIM` until
   the operator answers, then become `unverified-here` if the source stays out of reach.

Log each tier tried: the query, date and result. One failed search is not an
acquisition pass. Searches use the citation and general terms only: never internal
IDs, unpublished results or data from the product (`data-access.md`).

Every acquired source the review quotes is dumped with `pdftotext -layout` into
`review/extracts/`; quote checks read only those dumps.

## Source identity

Record for every acquired item: title, authors or issuing body, journal or series,
year, volume and pages, version (a preprint is not the published article; a protocol
version 2.0 is not version 1.3), the evidence that it is the cited item, the file hash,
and where and when it was obtained. Do not infer identity from a file name.

## Checking a value against its source

For each planning value or effect the product attributes to a source:

1. Locate the value in the source: table, figure or text, with page.
2. Record the population, intervention, comparator, endpoint definition, time point
   and analysis set the source reports it for.
3. Where the product derives the value (pooling arms, weighting by case mix,
   converting a median to a rate), recompute the derivation from the source's numbers
   in a script.
4. Classify: the source contains the value as used; contains it for a different
   population, endpoint or time frame (transported); contains a range the value sits
   in, and where; does not contain it.

## Checksum-constrained transcription

When a source table has totals, transcribe the cells needed and the printed totals
separately, and require the transcribed cells to sum to the totals. Never replace a
printed total with a computed one; a source whose own arithmetic fails is recorded as a
property of the source.

## Quotations

Locate each quotation in the extract, confirm the wording on the page, cite the
printed page, and record any ellipsis. Text extraction locates; the page decides.
