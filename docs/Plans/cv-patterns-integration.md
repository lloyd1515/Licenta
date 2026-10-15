# 5 "AI CV" patterns → Licenta repo: integration plan

Date: 2026-10-14. Arena: 4 Sonnet runners, 1 Sonnet cross-judge, synthesized by parent. Synthesis note at the end.

## TL;DR

Only **pattern 4 (eval harness + gated CI)** fits this repo honestly, and in a DSP form with no LLM judge. Patterns 1, 2, 5 go in separate repos (or into existing agent repos). Pattern 3 gets dropped. Your gap is eval rigor and tests, not agents. You already have agent projects (Agentic Goal Extraction with HITL and 227 tests, AutoResearcher, local_agent).

## Fact-check of the pasted claims

Verdict: **Mostly true on direction, overstated on evidence.**

- ✅ Evals and measurement as the differentiator: several hiring-side sources say this, though most are course or vendor blogs, not surveys ([Gauntlet](https://gauntletai.com/night-school/what-hiring-managers-actually-look-for-in-ai-engineers)).
- ✅ Agentic demand is rising: Stanford AI Index 2026 / Lightcast puts agentic skills at 0.06% → 0.23% of US postings (2024→2025). Growth is fast but the absolute share is small ([Lightcast](https://lightcast.io/resources/blog/stanford-ai-2026)).
- ✅ DeepMind Polaris exists: a coding-agent eval team, recruiting since Sept 2026 ([Digg](https://digg.com/ai/nvg3daqd)).
- ⚠️ HubSpot story: the engineer's project was an LLM code-documentation tool, not a "personal AI-agent" ([Business Insider via AOL](https://www.aol.com/news/im-ai-engineer-hubspot-r-094901635.html)).
- ⚠️ Petersson/OpenAI: self-reported via podcast. He had prior jobs at Midjourney and Dataland and has since left OpenAI ([Fortune](https://fortune.com/2026/03/29/gen-z-high-school-dropout-gabriel-petersson-openai-researcher-six-figures-advice-for-young-people-silicon-valley-jobs)).
- ⚠️ The "Landed" repos exist (13-project and 85+-project lists), but the exact repo name was not confirmed ([GitHub topic](https://github.com/topics/llm-projects)).
- ❌ "Strong patterns in hiring data": no actual hiring dataset is cited, only practitioner opinion.

Relevance to your targets (Arobs, Bending Spoons, FME, LSEG, Qubiz, Riverbed): these are mostly product, fintech and network companies, not frontier labs. Testing, CI and measurement discipline (pattern 4) transfers to all of them. Patterns 1/2/3 matter only for AI-engineer roles.

## Triage

| # | Pattern | Verdict | Where | Effort | Why |
|---|---|---|---|---|---|
| 4 | Eval harness + CI gate | **INTEGRATE** | this repo | M, 5–7 d | zero tests today (only screenshot suite); improves thesis defense ("how do you know it works?") |
| 5 | Company-specific agent | SEPARATE | new repo | M, 5–7 d | only once one employer reaches the interview stage; work backwards from their problem, not from CSI |
| 2 | Tool agent + pass@k | SEPARATE | existing Agentic Goal Extraction repo | S, ~1 d | add a pass@k harness there; a CSI agent here would be a thin wrapper with n=3 data |
| 1 | Hybrid RAG + evals | SEPARATE, optional | new repo | M, 6–8 d | the vault corpus is tiny → trivial recall; most commoditized pattern; needs a BM25-only baseline |
| 3 | Multi-agent orchestrator | **DROP** | — | — | DSP chain is linear and deterministic; a supervisor would be theatre and the "retro" fiction |

## Pattern 4: design (this repo)

Verified repo facts: no git; no `tests/`; pytest + pytest-cov in `.venv`; npz files 60–124 KB (safe to commit).

**Generator gap the candidates missed.** `synthetic_gen.generate_ground_truth(duration, fs)` hardcodes **one** scenario: still 0–3 s, walking 3–10 s, fall at 10 s, on the floor until 20 s. It uses global `np.random` (lines 170–176) and takes no seed. A synthetic false-alarm rate is therefore impossible today, because no no-fall synthetic scene exists. This is why the effort is 5–7 d, not 3–4.

Steps (each → verify):

0. `git init`, first commit of the current state → verify: `git log` shows a baseline commit.
1. **Seeding.** Add an optional `rng: np.random.Generator | None = None` to `simulate_csi_dataset`, keeping default behaviour → verify: same seed gives identical arrays, and `run_simulation.py` output is unchanged.
2. **Scenario library** in a new `src/dsp_lab/scenarios.py` (keep `generate_ground_truth` untouched): walk-only, sit-down (slow descent), lie-down (slow), fall at variable t, empty room → verify: each returns a `GroundTruth` with a correct `fall_impact_idx` or none.
3. **Characterization tests** pinning `hampel_filter_1d`, `butterworth_bandpass`, `compute_pca_first_component` and `compute_doppler_spectrogram` (a known sinusoid should give a known peak), with edge cases (empty, NaN, short) → verify: `pytest` passes.
4. **Real-data smoke gate**: A → no alarm, B → no alarm, C → alarm (`allow_pickle=True`). Label it "n=3, regression guard, not validation" → verify: passes on current code.
5. **Monte-Carlo sweep**: scenarios × SNR {0,5,10,20,30} dB × outliers on/off × K seeds. Output `eval/results.json` with detection rate, false-alarm rate, latency p50/p95, and **Wilson CIs** → verify: rerunning with the same seeds gives identical JSON.
6. **Sensitivity sweep** over `TH_DERIVATIVE`, `TH_DOPPLER_HIGH`, `DORMANCY_WINDOW_SEC` and `TH_DORMANCY_VAR`. Explicitly report the activity-gate split (0.20 synthetic vs 11.0 hardware, `fall_detector.py`): the thresholds are tuned to the simulator. That is a finding, not a bug to hide.
7. **Gate**: committed `eval/baseline.json`, plus `eval/check.py` that exits nonzero on regression beyond tolerance. Run it from GitHub Actions if you push to a remote, otherwise from `make eval` or a pre-commit hook → verify: a deliberately broken threshold fails the gate.

**Thesis safety.** Run steps 5–6 **before** the defense. If results contradict the README/thesis numbers (2.54 s, 48.5 Hz, 0.043 m are simulation-only), put them in Limitations and tell the professor. Never edit thesis numbers silently. Simulated pass rates are **self-consistency** (detector and simulator co-designed), not accuracy.

## Optional stretch (parent-added, from fact-check)

[Wi-Chat (arXiv 2502.12421)](https://arxiv.org/abs/2502.12421) prompts LLMs with Wi-Fi sensing physics to classify CSI zero-shot, falling included. It is a preliminary study. Running a Wi-Chat-style LLM classifier as a **baseline against the FSM inside the step-5 harness** would be the only honest LLM touchpoint: an LLM-vs-deterministic comparison with CIs, where a negative result is still a result. It costs about M, 3–4 d, plus API spend. Do it only after pattern 4 is done, keep it out of the thesis unless the professor agrees, and treat it as a portfolio/"future work" item.

## Sequence

1. Week 1–1.5: pattern 4, steps 0–7.
2. +1 d: pass@k harness in the Agentic Goal Extraction repo.
3. When a specific interview lands: pattern 5 for that company, reusing the harness discipline.
4. Only if time remains: Wi-Chat baseline, then RAG. Drop 3.

## CV bullets (fill only with measured numbers)

- "Built a regression-gated eval harness for a Wi-Fi CSI fall-detection FSM: <N> seeded synthetic scenarios × <K> seeds with Wilson CIs, threshold-sensitivity analysis, CI blocks regressions; <T> tests, <C>% coverage."
- (if stretch done) "Benchmarked a zero-shot LLM CSI classifier (Wi-Chat-style) vs a deterministic FSM: detection <X>% vs <Y>%, false alarms <A> vs <B>, on <N> synthetic scenes."

## Do NOT claim

- "LLM-/AI-powered fall detection", "agentic CSI system", "multi-agent" anything for this repo.
- Real-world accuracy: real data is n=3 recordings with 1 fall. 2.54 s, 48.5 Hz and 0.043 m are **simulation**.
- Simulated detection rate presented as accuracy: it is self-consistency.
- LLM-as-judge calibration: none is used here.
- pass@k or recall@k without stating n and a baseline.
- Any Bluetooth triangulation result (see the 17 Jun data limit and MDPI overlap).

## Synthesis note

- **Base:** candidate 2. Cross-judge 28/30, top score, and my own pick agreed. It had the most realistic prerequisites and the best "do not claim" section.
- **Convergence:** all 4 runners independently reached the same shape: 4 = integrate (DSP form, no LLM judge), 3 = drop, 1/2/5 = separate. Consensus shape shipped.
- **Grafts:** C1, thresholds tuned to the simulator reported as a finding (activity-gate 0.20 vs 11.0). C3, pass@k moved into the existing agent repo and the "self-consistency, not accuracy" label. C4, Wilson CIs. Cross-judge, the defense-contradiction risk, which became the thesis-safety rule.
- **Parent additions (verified in code):** the generator hardcodes a single fall scenario with no seed, so a scenario library is needed and the effort went from 3–6 d to 5–7 d. Also the Wi-Chat stretch, from the fact-check.
- **Rejected:** C4's thin "experiment assistant" agent (duplicates existing repos). C1's fall-timing and localization-RMSE sweep axes (need plumbing not worth it: `localization.py` is not wired to the FSM). Bootstrap CIs (C2) dropped in favour of Wilson CIs, which suit binomial rates.
- **Dropouts:** none.
- **Verification:** every function, constant and file claim was re-checked against `src/dsp_lab/` (grep of defs, `synthetic_gen.py:46-176`, npz sizes, `.venv` packages). The plan claims no measured results; all numbers are placeholders.
