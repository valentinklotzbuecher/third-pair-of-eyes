---
name: statements
description: >-
  Third review stage: build the statement ledger, one row per load-bearing statement
  of the product (result, calculation, planning assumption, specification or
  interpretation), recording how central it is, whether it holds, what survives, what
  is not established and the strongest defence; and draft the answers to the
  questions in the assignment. Records what is true; rates nothing.
---

# Statements

A printed number is not a finding, and a plan is not adequate because it is written
down. Work from the surviving evidence to what each statement of the product can carry,
then test it.

## Start from the artifacts

Read `analysis/code-and-data/results.csv`, `spec-map.csv`, `assumption-ledger.csv`
(where it exists), `analysis/document/*.csv`, the stage reports and the module reports:
the files, never a remembered number. Screen every result row:

- `validity` not `clean` → evidence that the procedure is uninformative here, never a
  test outcome. `unvalidated` rows cannot carry a statement yet.
- `row_role = rebuttal` → a re-run of the product's own number: if it holds, it cannot
  settle a statement; if it fails (the number does not reproduce, or the
  recomputation disagrees), it counts against.
- `data_mode = synthetic` → evidence about code behaviour only.
- `state = DATA_NOT_SHARED` → the statement's printed number is `unverified-here` for
  that reason; its arithmetic, consistency and specification are still decided on the
  evidence that exists.
- Scope assumptions in earlier reports carry into every row that relies on them; if
  one was overturned, re-derive or flag what depended on it.

## The statement ledger

Go through the product's summary, conclusions and the sections its profile names
(`../references/product-profiles.md`) sentence by sentence, then the tables those
sentences rest on. One row per load-bearing statement, in `review/statements-REPORT.md`
and `analysis/statements/statement-ledger.csv` (template
`../assets/statement-ledger.csv`). For a short product keep at most 15 rows: fold
statements that stand or fall together into one row:

`row_id | kind | statement | location | centrality | holds | kernel | not_established |
strongest_defence | defence_tested | status | evidence`

IDs run `ST01, ST02, …`. One sentence becomes several rows when its parts stand on
different evidence; each row quotes the sentence.

- **`kind`**:
  - `result`: an estimate, a test result or a descriptive number the product reports;
  - `calculation`: a number the product derives from other numbers (a sample size, a
    power, an expected rate, an inflation for dropout);
  - `assumption`: a planning value or modelling premise a calculation rests on;
  - `specification`: a pre-specified element of the design or analysis (an estimand
    attribute, an analysis set, a model, a rule for missing data, a stopping rule);
  - `interpretation`: what the product concludes or recommends from its numbers.
- **`centrality`**, read from where the statement sits and what rests on it:
  - `primary`: the product's main output (an SSE's target N with its power and effect;
    a SAP's primary estimand and primary analysis; a report's primary result and its
    conclusion; a manuscript's abstract and conclusions);
  - `supporting`: a statement a primary one rests on (a planning value, a key
    secondary result, a sensitivity analysis the product cites in support, an
    analysis-set rule, a randomisation detail the analysis depends on);
  - `peripheral`: background, exploratory or descriptive statements no primary
    statement rests on.
- **`holds`**, one of the three words below. What they mean depends on the kind:
  - `holds`: a result or calculation is reproduced, recomputed or arithmetically
    consistent, and the statement says no more than it shows; an assumption is sourced
    and the source supports it for this population, endpoint and time frame; a
    specification is complete, unambiguous, consistent with the governing documents
    and fit for the estimand it serves; an interpretation follows from the evidence as
    printed. A gap that changes no reader's understanding (a disclosed choice, a
    nuance) still holds.
  - `narrower`: the statement's point stands only in a narrower scope, size,
    population, scenario or certainty than printed, and the product does not say so
    (a power that holds only under the most favourable planning value; an assumption
    whose source covers a different population; a specification fit for a different
    estimand from the one stated; a conclusion wider than its analysis set).
  - `not established`: the evidence does not deliver the statement's point: the
    number does not reproduce or recompute; an assumption has no source, or its source
    does not contain it; a specification is missing, ambiguous in a way that changes
    the result, or contradicted by a governing document or by the product itself; an
    interpretation needs evidence the product does not have. This is the finding, not
    a softer one, because the burden is the product's.
- **`kernel`**: what the evidence does support, stated as what it is (for `not
  established`, the weaker statement that survives, or "none"). **`not_established`**:
  what the statement asserts beyond the kernel. Both are written so a reader can quote
  them.
- **`status`**: `settled`, `INTERIM` (a feasible decisive check is unrun), `untested`
  (no valid direct check exists), `unverifiable` (the product's materials make the
  check impossible: a finding) or `unverified-here` (data not shared under the job's
  data mode, or a source the review could not obtain: a limit on the review).
- **`strongest_defence`**: the best case the statistician could make. Testable but not
  yet run → the row is `INTERIM`, in either direction. A defence resting on materials
  the product does not supply (an unnamed source, a simulation result with no code)
  shields nothing: the missing material is its own finding. Any other untestable
  defence that the documents support and that would account for the evidence is
  recorded beside the row and keeps it from `not established`. A defence tested and
  failed is recorded as failed.

**Self-contradictions.** Where the product states one element two ways (an endpoint
window, a block size, a planning value in a caption), the row for that element records
which version the code implements and whether the other is an isolated slip. If the
code and every other mention agree, the element `holds` and the slip is a finding on a
row that holds; if the versions compete (the code uses one, the protocol the other),
the element is `not established` until the statistician says which is meant.

**A plan is judged as a plan.** A SAP or protocol specification is not "not
established" because no data exist yet; it is judged on completeness, clarity,
consistency and fitness for its estimand. A sample size is judged on its calculation
and its assumptions, not on whether the trial will recruit.

**Guard both directions.** Good code and careful writing are not evidence for a
statement; equally, do not inflate a narrower-but-true statement into one not
established. A defence that accounts for the evidence resolves the attack or narrows
it.

## The work

1. **Decompose what drives each primary calculation or result**: which planning
   values move the sample size most, which analysis choices move the estimate, in
   `analysis/statements/driver-matrix.csv` (template `../assets/driver-matrix.csv`).
2. **State the supportable version** of each primary statement: what N gives what
   power for what effect under which assumptions; what the primary analysis estimates
   and under which handling of intercurrent events; what the result shows, for whom,
   how large, against what comparator, with what uncertainty.
3. **Test it** (`../references/statement-test-matrix.md`): printed contradictions and
   version leads from `document`; each assumption against its source
   (`../references/source-protocol.md`; for planning values and effect sizes, the
   independent literature, `../references/literature-protocol.md`); design validity;
   whether a conclusion reaches beyond its evidence (a non-significant difference
   read as equivalence, a subgroup read as an effect, an association read as cause).
4. **Try to overturn your own verdict**, in whichever direction it runs: for each
   primary statement, run one defensible challenge that could reverse the row and
   record the result.

## The assignment questions

For every question `Q1, Q2, …` in `00_INTAKE.md`, draft an answer in
`analysis/statements/questions.csv` (template `../assets/questions.csv`): `q_id |
question | answer | basis | status | evidence`, where `basis` names the rows,
findings and checks the answer rests on and `status` is `answered`, `partly answered`
(say what is missing) or `cannot be answered from the materials` (say what would
answer it). An answer is evidence-led and direct ("Yes: under the stated control
rates between 0.35 and 0.45 the required N moves by at most 6, while a hazard ratio of
0.70 instead of 0.62 raises it to 412 (work/logs/ss_sensitivity.log)"), and it answers
the question asked, including when the answer is "no" or "it depends on X". A question
that asks for a judgement the evidence cannot settle (how much to write about an
assumption) is answered with the evidence that bears on it and marked `partly
answered`. The verdict stage decides the final answers.

## Output

`review/statements-REPORT.md` from `../assets/report-template.md`: findings `S1, S2, …`,
then the supportable version of each primary statement, the statement ledger table
(with `Centrality` and `Holds` columns; later tools read them), the statement-test
matrix and the draft answers. New anomalies or computations needed go back to
`code-and-data`; once they land, refresh the affected rows before the challenge.
