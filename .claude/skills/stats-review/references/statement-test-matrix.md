# Statement-test matrix

One row for every material proposition in the supportable version of each primary
statement, as a table in `review/statements-REPORT.md`. Adapted from the upstream
claim-test matrix.

| Field | Meaning |
|---|---|
| row_id | the statement-ledger row the proposition belongs to |
| proposition | one falsifiable statement |
| role | calculation input, calculation, specification, result, interpretation, design validity, framing |
| evidence | the exact script and log, recomputation, specification-map row, or printed location |
| source | the cited work and page, for planning values and external claims |
| independence | independent, partly independent, dependent, unknown (`literature-protocol.md`) |
| result | supports, contradicts, qualifies, not addressed, blocked, unverified-here |
| effect on statement | the clause retained, narrowed, replaced or removed |
| status / defence | the ledger status (settled, INTERIM, untested, unverifiable, unverified-here); the strongest defence and whether it was tested |

## Calculation chains

Split a sample size statement into at least:

1. each planning value → its source;
2. the effect → its clinical and empirical rationale;
3. the inputs → the calculation (method, test, sidedness, units);
4. the calculation → the evaluable N;
5. the evaluable N → the randomised N (dropout allowance, rounding);
6. the calculation's test → the planned primary analysis.

A recomputation that agrees fills only rows 3 and 4.

## Result chains

Split a result statement into the estimand, the analysis set, the estimate with its
interval, the handling of missing data and intercurrent events, and the
interpretation. "Significant" fills only the estimate row; "effective" needs every
row.

## Framing comparison

Extract the statement from each place it appears rather than paraphrasing the product
as one undifferentiated conclusion. A product can be careful in a table note and
expansive in its summary; that difference is part of the result.
