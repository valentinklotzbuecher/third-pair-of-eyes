# Worked cases

Stylised composite cases that show the procedures at work. They are not records of any
real review; verify every new case on its own evidence.

## A caption that disagrees with the text

*Case: an SSE plots power against N for the planning values "S_ctrl = 0.40,
S_trt = 0.57". The figure caption gives 0.58 for the treatment arm; the text, the
summary and the code use 0.57.* The printed-consistency walk records three agreeing
mentions and one disagreeing caption; the specification map shows the code uses 0.57.
The planning-value row holds; the caption is a finding on a row that holds, `where:
text`, fixed by correcting the caption. Had the code used 0.58 while the text said
0.57, the row would be `not established` until the author said which value is meant,
and the finding would be `where: unresolved`.

## Units in an event-driven sample size

*Case: the primary endpoint is event-free survival from day 61 to day 365 after a
procedure, a window of 304 days. Planning values are stated as 12-month event-free
proportions. A design function is called with the event probabilities at its default
`eventTime = 12` while accrual and follow-up are entered in days.* The design function
then reads the probabilities for the 304-day window as probabilities at day 12, and
the hazards it derives are about 25 times (304 / 12) too large; the event count and N it returns are not
the trial's. The independent recomputation (exponential hazards from the 304-day
proportions, Schoenfeld's formula for events, the event probability over the window)
gives a different N; the difference traces to the units, not to the method. Lesson:
time units are inputs of the recomputation, written into the design question, not a
detail to check afterwards.

## Inflating for dropout

*Case: 84 evaluable participants, 10% expected without an evaluable endpoint, target
"84 × 1.10 = 93, rounded to 100".* 84 / 0.90 = 93.3, so 94 is the minimum; rounding to
100 covers both, and the printed target holds. The text's formula is still wrong and is
a finding on a row that holds (`where: text`). Had the target been 93, the randomised N
would have been `not established` at the stated dropout rate.

## A calculation for one test, an analysis with another

*Case: the sample size simulates an unadjusted Welch interval for a mean score; the SAP
plans a linear model adjusted for the stratification factors with a robust interval.*
The product says the unadjusted interval is a conservative approximation. Covariate
adjustment for prognostic stratification factors does not reduce power in expectation,
so the direction is right and the statement holds as a planning approximation; the
review records it, and adds a finding only if the robust variance estimator the SAP
names is known to be anti-conservative at the planned N, quantified.

## A filter that drops missing values

*Case: a report's analysis set is "all randomised participants with a baseline
measurement". The code filters `baseline > 0`.* On the synthetic `edge` dataset, two
participants with a missing baseline and one with a baseline of exactly 0 are planted;
the expected analysis set excludes the two missing ones only. The code excludes all
three (`filter()` drops the `NA` rows and the zero). The printed N cannot be checked
without data, but the code does not implement the printed definition: a finding,
`where: code`, established without patient data.

## A recomputation that agrees for the wrong reason

*Case: the review recomputes an SSE's N with a closed form and gets the printed N to
the participant, taking the control-group rate from the product's code.* The cited
source reports a rate of 0.35 for a comparable population, not the 0.40 in the code.
The challenge stage rules the agreement a check of arithmetic only: the planning value
is `TRANSPORTED` or `UNANCHORED` depending on what the source contains, and the
recomputation with the source's value is the one that bears on the statement.

## A noisy grid

*Case: a simulated sample size picks the first grid point whose simulated power
reaches 80% at 5,000 replicates per point, and the text calls the N "approximate".* A
fitted power curve over the grid puts the crossing one grid step later. The product
already says the N is approximate; the review engages that statement on its terms: the
finding is that the approximation runs in the unfavourable direction by one grid step,
with the fitted crossing and its Monte Carlo interval, not that the N is wrong.

## A planning value from another population

*Case: a control-group toxicity rate is taken from trials in metastatic disease and
applied to an adjuvant population with shorter, less intensive treatment.* The value is
`TRANSPORTED`. The sensitivity of N to it decides what it costs: if a plausible
adjuvant rate moves N by a few participants, the row holds with a note; if it moves N
beyond recruitment, the sample-size statement is `narrower` (it holds for the cited
population's rate only).
