---
name: prediction-model-diagnostics
description: >-
  Diagnostics for clinical prediction and prognostic models and for diagnostic
  accuracy studies: sample size for development, predictor handling, overfitting and
  shrinkage, internal and external validation, calibration and discrimination,
  clinical utility, and reporting against TRIPOD+AI or STARD. Invoke from
  `code-and-data` whenever a product develops, validates or updates a prediction model,
  or estimates diagnostic accuracy.
---

# Prediction-model diagnostics

A prediction model is judged by how well it predicts in new patients, not by its
coefficients. Most failures are overfitting that internal performance hides, and
calibration that nobody checked.

Trigger: development, validation or updating of a prediction or prognostic model; a
risk score; a diagnostic accuracy estimate. `NOT_APPLICABLE` otherwise.

## Core checks

- **Sample size for development.** The number of events and candidate predictor
  parameters against the criteria of Riley et al. (2020): shrinkage factor of at least
  0.9, small optimism in apparent R², precise estimate of the overall risk. Events per
  variable rules of thumb are a floor, not a justification. Candidate parameters count
  every degree of freedom (spline terms, categories, interactions), including those
  considered and dropped.
- **Predictors.** Defined and measured as they would be at the moment of prediction in
  practice; no predictor that uses information from after that moment (leakage);
  continuous predictors kept continuous with flexible form rather than categorised;
  predictor selection by univariable significance or stepwise methods flagged, and if
  used, repeated inside the validation.
- **Missing data.** Multiple imputation in development, with the outcome in the
  imputation model; how missing predictors will be handled when the model is used.
- **Validation.** Internal validation by bootstrap (repeating every modelling step,
  including selection and imputation, in each bootstrap sample) or cross-validation,
  reporting optimism-corrected performance; a single random split wastes data and is
  noisy at the sample sizes typical for single-centre studies. External validation in
  a different population or period where the claim is generalisability.
- **Performance.** Calibration first: calibration plot (smoothed), calibration slope and
  intercept (calibration-in-the-large) (Van Calster et al. 2019); discrimination (c
  statistic with interval); overall measures (Brier score). A c statistic alone is not
  validation. Shrinkage or recalibration applied where the slope is below 1.
- **Clinical utility.** Decision-curve analysis or net benefit at clinically relevant
  thresholds, where the product claims usefulness for decisions.
- **Presentation.** The full model (all coefficients with the intercept or baseline
  hazard) so it can be validated by others; TRIPOD+AI items for the claims made.
- **Diagnostic accuracy.** Reference standard and its blinding, the spectrum of
  patients, partial or differential verification, sensitivity and specificity with
  intervals, prevalence-dependent measures (predictive values) reported for the
  stated prevalence, and the STARD 2015 items the claims rest on.

## Report back

Lead with overfitting risk (development sample size against the number of candidate
parameters), the validation design, calibration, and any leakage. Account for
coverage. Put each under `## Leads for later stages` for `statements`.
