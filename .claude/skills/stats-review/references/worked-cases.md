# Worked cases

Stylised composite cases that show the procedures at work. They are not records of any
real review, and their numbers are invented; verify every new case on its own
evidence, and do not look for these patterns in a product because they appear here.

## A footnote that disagrees with the text

*Case: a SAP defines the primary endpoint at day 28 with a visit window of ± 3 days in
the text; the footnote of a mock table says ± 7 days.* The consistency walk records
both locations; the derivation code delivered with the SAP uses ± 3. The specification
row holds (text and code agree) and the footnote is a finding on a row that holds,
`where: text`. Had the code used ± 7 while the text said ± 3, the row would be `not
established` until the author said which window is meant, and the finding would be
`where: unresolved`.

## Units in an event-driven sample size

*Case: time to first exacerbation over 48 weeks. The cited trial reports event-free
proportions at 48 weeks; the design function is called with those proportions while
its event time is left at the default of 12 and accrual and follow-up are entered in
weeks.* The function reads the 48-week proportions as proportions at week 12, so the
hazards it derives are four times too large and the event count and N it returns
belong to a different trial. The independent recomputation (exponential hazards from
the 48-week proportions, Schoenfeld's formula for events, the event probability over
the accrual and follow-up pattern) gives another N; the difference traces to the
time unit, not to the method. Lesson: time units and horizons are inputs of the
recomputation, written into the design question, not details checked afterwards.

## Inflating for dropout

*Case: 128 evaluable participants, 15% expected dropout, target "128 × 1.15 = 148".*
128 / 0.85 = 150.6, so 151 is the minimum at the stated dropout rate; 148 randomised
yields about 126 evaluable. The randomised-N statement is `narrower` (it holds for a
dropout rate up to about 13.5%), and the finding is `where: text and code` when the
code multiplies too.

## A calculation for one test, an analysis with another

*Case A: the sample size is for a two-sample t-test on the 6-month value; the SAP plans
an ANCOVA adjusting for the baseline value.* With a positive correlation between
baseline and follow-up, the ANCOVA needs fewer participants, so the calculation is
conservative; the statement holds when the product says so, and a missing sentence is
a text finding at most. *Case B: the calculation assumes the ANCOVA gain (correlation
0.6), but the SAP's primary analysis is a rank test on change scores.* The power the
calculation promises is not delivered by the planned analysis: a finding against the
sample-size statement, quantified by simulating the planned analysis.

## A filter that drops missing values

*Case: a report's analysis set is "all randomised participants with a baseline
measurement". The code filters `baseline_value > 0`.* On the synthetic `edge` dataset,
two participants with a missing baseline and one with a baseline of exactly 0 are
planted; the expected analysis set excludes the two missing ones only. The code
excludes all three (`filter()` drops the `NA` rows and the zero). The printed N cannot
be checked without data, but the code does not implement the printed definition: a
finding, `where: code`, established without patient data.

## A recomputation that agrees for the wrong reason

*Case: the review recomputes an SSE's N with a closed form and gets the printed N to
the participant, taking the standard deviation from the product's code (12 mmHg).*
The cited trial reports 15 mmHg for the same outcome in a comparable population. The
challenge stage rules the agreement a check of arithmetic only: the planning value is
`TRANSPORTED` or `UNANCHORED` depending on what the source contains, and the
recomputation with the source's value is the one that bears on the statement.

## A noisy grid and a smoothed curve

*Case: a cluster-randomised trial's number of clusters is chosen as the first grid
point whose simulated power reaches 90%, at 1,000 replicates per point, and the power
figure is drawn with `cummax()` so that it never decreases.* A power curve fitted to
the raw grid output crosses 90% one cluster per arm later than the product's choice,
with a Monte Carlo interval that excludes the chosen number. The finding is that the
chosen number is optimistic by about one cluster per arm; the smoothed figure is a
second finding where the text reads values off it.

## A planning value from another population

*Case: a 30-day readmission rate taken from a national registry is applied to a single
tertiary centre whose case mix differs.* The value is `TRANSPORTED`. The sensitivity of
N to it decides what it costs: if a plausible local rate moves N by a few
participants, the row holds with a note; if it moves N beyond recruitment, the
sample-size statement is `narrower` (it holds for the registry's rate only).
