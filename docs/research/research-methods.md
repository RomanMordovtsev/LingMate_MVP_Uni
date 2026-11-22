# Research notes: Research Methods in SLA (LAMS, UPV/EHU, 2026–27)

Course by María Martínez Adrián. Distilled from Units 1–6 handouts (Unit 5: qualitative and mixed methods, classroom research; Unit 6: quantitative designs and statistics), slides on designs, reliability, validity and statistical tests, answer keys for the Unit 4 and Unit 6 exercises, Brown & Rodgers (2002, ch. 1), Mackey & Gass (2005, ch. 4–7). Course is still running.

## How to evaluate LingMate features properly

1. **Define variables.** For each pedagogical feature, name the independent variable (e.g. feedback type: recast vs prompt), the dependent variable (e.g. accuracy on a target form in later free production), and control variables (scenario, level, time on task).
2. **Reliability first.** Use a fixed, versioned test set of learner utterances with gold-standard corrections (roadmap 5.3) so prompt/model changes are compared on the same data. Report agreement/precision/recall per error category.
3. **Validity.** Measure what matters: accuracy in *free production* (sla.md §6), not only quiz scores. Beware internal-validity threats (practice effects, novelty) and external-validity limits (one user ≠ all users).
4. **Longitudinal case data.** LingMate's logs are a longitudinal case study of interlanguage development — rare in CALL research (Gillespie 2020). Keep timestamps and versions so trends are interpretable.
5. **Ethics.** Informed consent for using learner data, anonymisation, data minimisation, the right to delete. Required before any research use or multi-user release.
6. **A/B testing later.** When there are several users, run simple experiments (randomised feature flags) with pre-registered metrics (learning + engagement, engagement.md §9).

## Designs and measures (Units 5–6)

7. **Single-learner time-series design.** Mackey & Gass (2005), Unit 6: with one or few learners, measure several times before a change (baseline O1–O5), introduce it, then measure several times after (O6–O10). Repeated baselines raise internal validity; maturation stays a threat.
   - **Design rule:** when a feature is switched on for Roman (e.g. prompts instead of recasts for one error category), log the date and keep a weekly per-category accuracy series, so the weekly report can show "before vs. after" honestly. Add a delayed check (2–4 weeks later), since immediate gains fade.
8. **Comparable pre/post tests.** Unit 6: a harder pretest makes gains look bigger; fix it by randomly splitting items between pre- and post-test per learner, or by balancing item difficulty.
   - **Design rule:** placement re-checks (C.2) and unit mastery checks (C.4) draw from item pools of calibrated difficulty, not the same fixed items, so practice effects don't inflate progress.
9. **Complexity, accuracy, fluency (CAF).** Unit 6 exercise key: accuracy (error-free T-unit ratio, errors per 100 words, % correct verb forms, accuracy of a target form), complexity (mean length of T-unit, clauses per AS-unit, subordination ratio, type–token ratio), fluency (speech rate, pauses, repairs).
   - **Design rule:** compute simple written CAF indices from the learner's chat turns (errors per 100 words from the error log, mean length of utterance, subordination markers, type–token ratio) and show them as trends, not grades. Accuracy alone can rise while learners avoid hard structures (morphosyntax §10).
10. **Reliability and validity of the eval.** Slides: inter-rater and intra-rater reliability, test–retest, internal consistency; content, face, construct, internal and external validity. Unit 4 key: blind rating protects internal validity.
    - **Design rule:** when Roman (or a second rater) labels eval cases, rate blind to the model name and re-rate a sample later (intra-rater check); report agreement before trusting a model comparison.
11. **Qualitative and mixed data.** Unit 5: case studies, diaries, stimulated recall, uptake sheets (learners note what they noticed in a lesson); triangulate numbers with the learner's own account; observer's paradox / Hawthorne effect.
    - **Design rule:** an optional one-line "what did you notice today?" uptake prompt at the end of a session, stored next to the metrics, gives the qualitative side of the weekly report.
12. **Questionnaires.** Unit 6 extra copies: Likert scales (e.g. willingness to communicate, MacIntyre et al. 2001), open items for attributions of success (Graham 2004).
    - **Design rule:** a short, optional monthly check-in (anxiety, enjoyment, willingness to speak in real situations) uses Likert items, so engagement claims rest on data (sla §2, engagement §9).
13. **Statistics cheat sheet** (slides): correlation (2 numeric), regression (prediction), t-test (numeric × 2 groups), ANOVA (numeric × 3+ groups), chi-square (2 categorical). With a single user, prefer descriptive trends plus time-series reasoning to significance tests.

