# Clinical guidelines and method sources

A map from product and design to the guidance a review reads it against, and the
method sources the modules cite. A guideline item is a lead: it becomes a finding only
when a load-bearing statement depends on it (`../document/SKILL.md`, section 3). Open a
source before attributing content to it in a finding; an abstract or this map is not
the source.

## Regulatory and harmonised guidance

| Guidance | Use it for |
|---|---|
| ICH E9, Statistical principles for clinical trials (1998) | analysis sets, prespecification, covariate adjustment, multiplicity, interim analyses, the language of confirmatory claims |
| ICH E9(R1), Addendum on estimands and sensitivity analysis (Step 4, November 2019) | the five estimand attributes, intercurrent-event strategies, sensitivity versus supplementary analyses (`estimands.md`) |
| ICH E3, Structure and content of clinical study reports (1995) | what a report should contain, participant flow, deviations |
| ICH E10, Choice of control group (2000) | non-inferiority margins, assay sensitivity |
| ICH E6(R3), Good clinical practice | data integrity and record-keeping context |
| ICH E20, Adaptive designs for clinical trials | draft (Step 2, June 2025); check the ICH site for its current status before citing it as final |
| EMA guideline on adjustment for baseline covariates in clinical trials (EMA/CHMP/295050/2013) | prespecified covariates, stratification factors in the analysis |
| EMA guideline on missing data in confirmatory clinical trials (EMA/CPMP/EWP/1776/99 Rev. 1, 2010) | missing-data assumptions, single imputation, sensitivity analyses |
| EMA guideline on multiplicity issues in clinical trials (draft, EMA/CHMP/44762/2017) | families, co-primary endpoints, secondary claims |
| EMA guideline on the investigation of subgroups in confirmatory clinical trials (EMA/CHMP/539146/2013) | subgroup claims |
| EMA guideline on the choice of the non-inferiority margin (EMEA/CPMP/EWP/2158/99) | margins |
| FDA guidance: Adjusting for covariates in randomized clinical trials for drugs and biological products (2023) | covariate adjustment, marginal effects for non-collapsible measures |
| FDA guidance: Multiple endpoints in clinical trials (2022); Non-inferiority clinical trials (2016); Adaptive design clinical trials (2019) | as named |
| Swiss Human Research Act and Clinical Trials Ordinance (risk categories A–C) | context only: the product's category is recorded at intake |

Regulatory guidance binds regulatory submissions. For investigator-initiated trials it
is the reference for good practice, not a requirement; a finding citing it says which.

## Reporting guidelines

| Product or design | Guideline |
|---|---|
| Protocol | SPIRIT 2025 (Chan et al., BMJ 2025;389:e081477) |
| Statistical analysis plan | Gamble C, et al. Guidelines for the content of statistical analysis plans in clinical trials. JAMA 2017;318:2337–2343 |
| Randomised trial report or manuscript | CONSORT 2025 (Hopewell et al., BMJ 2025;389:e081123) |
| Cluster randomised trials | CONSORT extension, Campbell MK, et al. BMJ 2012;345:e5661 |
| Non-inferiority and equivalence trials | CONSORT extension, Piaggio G, et al. JAMA 2012;308:2594–2604 |
| Pilot and feasibility trials | CONSORT extension, Eldridge SM, et al. BMJ 2016;355:i5239 |
| Crossover trials | CONSORT extension, Dwan K, et al. BMJ 2019;366:l4378 |
| Stepped-wedge trials | CONSORT extension, Hemming K, et al. BMJ 2018;363:k1614 |
| Adaptive designs | ACE, Dimairo M, et al. BMJ 2020;369:m115 |
| Observational studies | STROBE, von Elm E, et al. Lancet 2007;370:1453–1457 |
| Target trial emulation | TARGET statement (JAMA and BMJ, 2025) |
| Prediction models | TRIPOD+AI, Collins GS, et al. BMJ 2024;385:e078378 |
| Diagnostic accuracy | STARD 2015, Bossuyt PM, et al. BMJ 2015;351:h5527 |
| Choosing the target difference | DELTA², Cook JA, et al. BMJ 2018;363:k3750 |

## Method sources by topic

**Sample size.** Schoenfeld DA. Sample-size formula for the proportional-hazards
regression model. Biometrics 1983;39:499–503. Freedman LS. Tables of the number of
patients required in clinical trials using the logrank test. Stat Med 1982;1:121–129.
Borm GF, Fransen J, Lemmens WA. A simple sample size formula for analysis of covariance
in randomized clinical trials. J Clin Epidemiol 2007;60:1234–1238. Eldridge SM, Ashby D,
Kerry S. Sample size for cluster randomized trials: effect of coefficient of variation
of cluster size and analysis method. Int J Epidemiol 2006;35:1292–1300. Hooper R, et al.
Sample size calculation for stepped wedge and other longitudinal cluster randomised
trials. Stat Med 2016;35:4718–4728. Julious SA. Sample size of 12 per group rule of thumb
for a pilot study. Pharm Stat 2005;4:287–291. Riley RD, et al. Calculating the sample
size required for developing a clinical prediction model. BMJ 2020;368:m441.

**Simulation.** Morris TP, White IR, Crowther MJ. Using simulation studies to evaluate
statistical methods. Stat Med 2019;38:2074–2102. Landau S, Stahl D. Sample size and
power calculations for medical studies by simulation when closed form expressions are
not available. Stat Methods Med Res 2013;22:324–345.

**Estimands.** Kahan BC, et al. The estimands framework: a primer on the ICH E9(R1)
addendum. BMJ 2024;384:e076316. Clark TP, et al. Estimands: bringing clarity and focus
to research questions in clinical trials. BMJ Open 2022;12:e052953.

**Randomisation and covariates.** Kahan BC, Morris TP. Improper analysis of trials
randomised using stratified blocks or minimisation. Stat Med 2012;31:328–340. Senn S.
Testing for baseline balance in clinical trials. Stat Med 1994;13:1715–1726. Morris TP,
et al. Planning a method for covariate adjustment in individually randomised trials: a
practical guide. Trials 2022;23:328.

**Missing data.** White IR, Royston P, Wood AM. Multiple imputation using chained
equations: issues and guidance for practice. Stat Med 2011;30:377–399. Sterne JAC, et
al. Multiple imputation for missing data in epidemiological and clinical research:
potential and pitfalls. BMJ 2009;338:b2393. Cro S, et al. Sensitivity analysis for
clinical trials with missing continuous outcome data using controlled multiple
imputation: a practical guide. Stat Med 2020;39:2815–2842.

**Time to event.** Austin PC, Lee DS, Fine JP. Introduction to the analysis of survival
data in the presence of competing risks. Circulation 2016;133:601–609. Royston P, Parmar
MKB. Restricted mean survival time. BMC Med Res Methodol 2013;13:152. Schemper M, Smith
TL. A note on quantifying follow-up in studies of failure time. Control Clin Trials
1996;17:343–346. Grambsch PM, Therneau TM. Proportional hazards tests and diagnostics
based on weighted residuals. Biometrika 1994;81:515–526.

**Multiplicity and subgroups.** Bretz F, et al. A graphical approach to sequentially
rejective multiple test procedures. Stat Med 2009;28:586–604. Sun X, et al. Is a
subgroup effect believable? BMJ 2010;340:c117. Schandelmaier S, et al. Development of
the Instrument to assess the Credibility of Effect Modification Analyses (ICEMAN). CMAJ
2020;192:E901–E906. Jennison C, Turnbull BW. Group Sequential Methods with Applications
to Clinical Trials. Chapman & Hall/CRC 2000.

**Small samples and clusters.** Kenward MG, Roger JH. Small sample inference for fixed
effects from restricted maximum likelihood. Biometrics 1997;53:983–997. Pustejovsky JE,
Tipton E. Small-sample methods for cluster-robust variance estimation and hypothesis
testing in fixed effects models. J Bus Econ Stat 2018;36:672–683. Leyrat C, et al.
Cluster randomized trials with a small number of clusters: which analyses should be
used? Int J Epidemiol 2018;47:321–331. Altman DG, Bland JM. Absence of evidence is not
evidence of absence. BMJ 1995;311:485.

**Interval arithmetic.** Altman DG, Bland JM. How to obtain the P value from a
confidence interval. BMJ 2011;343:d2304. Altman DG, Bland JM. How to obtain the
confidence interval from a P value. BMJ 2011;343:d2090.

**Observational studies.** Hernán MA, Robins JM. Using big data to emulate a target
trial when a randomized trial is not available. Am J Epidemiol 2016;183:758–764. Austin
PC, Stuart EA. Moving towards best practice when using inverse probability of treatment
weighting (IPTW) using the propensity score. Stat Med 2015;34:3661–3679. VanderWeele TJ,
Ding P. Sensitivity analysis in observational research: introducing the E-value. Ann
Intern Med 2017;167:268–274.

**Prediction and Bayesian analysis.** Van Calster B, et al. Calibration: the Achilles
heel of predictive analytics. BMC Med 2019;17:230. Vehtari A, et al. Rank-normalization,
folding, and localization: an improved R-hat for assessing convergence of MCMC.
Bayesian Anal 2021;16:667–718. Kruschke JK. Bayesian analysis reporting guidelines. Nat
Hum Behav 2021;5:1282–1291.

The general-purpose cribs in `methods/` (Type S and M errors, the difference test,
forking paths, equivalence testing, bad controls, sensitivity to confounding, effect
sizes, randomisation inference, clustering, few clusters) come from the upstream
`research_skills` suite unchanged; `methods/README.md` lists them.
