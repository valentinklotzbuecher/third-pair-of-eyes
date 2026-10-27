# Audit cases

Failures that the audit's checks exist to catch. Stylised composites for clinical
products, in the spirit of the upstream "incident museum"; the SKILL.md carries the
rule, this file the shape of breaking it.

## Print fidelity

- **Planning value from the wrong table.** A review recomputed a sample size with the
  control rate from the "any grade" column where the product's calculation used the
  "grade 3 or worse" column; every "discrepancy" it reported was against a value the
  product never used.
- **A stale caption taken as the product's value.** A review built its recomputation on
  a figure caption's planning value; the text and the code used another.

## Row provenance

- **Right number, wrong analysis set.** A review's report cited a per-protocol estimate
  as the full-analysis-set result; the correct row existed in its results file.
- **Reduced-replicate number cited as a reproduction.** A simulated power from a
  1,000-replicate code-path check was compared with a printed 5,000-replicate power and
  called "not reproduced"; the difference was within Monte Carlo error.

## Propagation

- **Corrected input, stale consumers.** A corrected dropout allowance changed the
  randomised N in the summary row of the ledger but not in the answer to the
  assignment question that quoted the old N.

## Data mode

- **A synthetic result in the recomputation table.** A known-truth estimate from
  synthetic data appeared beside a printed estimate as if it checked it; synthetic runs
  never check printed numbers.
