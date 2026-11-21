# LLM Evaluation and Error Analysis Lab

[![Tests](https://github.com/sagarmandavkar-UX/llm-evaluation-lab/actions/workflows/tests.yml/badge.svg)](https://github.com/sagarmandavkar-UX/llm-evaluation-lab/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/Python-3.11-3776AB)
![Focus](https://img.shields.io/badge/Focus-AI_Measurement-7C3AED)
![License](https://img.shields.io/badge/License-MIT-green)

A model-evaluation framework for treating AI output as a measurable product surface. It compares candidate systems on quality, uncertainty, calibration, latency, cost, domain slices, difficulty, error types, paired item-level differences, and inter-rater reliability.

> Model labels and results are synthetic (generated with seed 11). They demonstrate evaluation design and do not benchmark or rank actual commercial models.

## Example result (synthetic data)

The seeded fixture contains 240 common evaluation items for each of three synthetic models. The `reasoning` system leads aggregate accuracy at **82.5%** (95% CI 77.5% to 87.1%), against 73.3% for `balanced` and 71.3% for `compact`, while the compact model is faster (about 421 ms median latency against 1,443 ms) and cheaper per correct answer. Inter-rater agreement is strong (Cohen's `κ ≈ 0.82`), but slice and error analyses show why aggregate accuracy is not a sufficient deployment criterion. Full output is in `outputs/`.

## Tech stack

Python 3.11, NumPy, pandas, Plotly and Streamlit. Tests use the standard library `unittest`, run in GitHub Actions, and the project ships with a Dockerfile and a Makefile.

## Decision question

Which candidate model meets the use case's minimum quality and safety requirements at an acceptable cost and latency—and which prompt slices still require human review?

## What this project demonstrates

- Versionable, item-level evaluation schema.
- Bootstrap 95% confidence intervals for accuracy.
- Paired bootstrap model comparisons on common prompts.
- Domain and difficulty scorecards.
- Factual, instruction, calculation, and citation error taxonomy.
- Cohen's kappa for inter-rater agreement.
- Confidence calibration through Brier score.
- Quality–cost–latency frontier.
- Interactive scorecard and downloadable evaluation set.

## Architecture

```mermaid
flowchart LR
    A[Versioned prompt set] --> B[Candidate model responses]
    B --> C[Blinded rubric scoring]
    C --> D[Agreement and adjudication]
    C --> E[Accuracy and calibration]
    C --> F[Error taxonomy and slices]
    E --> G[Paired comparisons]
    F --> H[Human-review policy]
    G --> I[Quality-cost-latency decision]
```

## Repository structure

```text
├── evaluation.py            # metrics, bootstrap inference, validation
├── app.py                   # interactive evaluation dashboard
├── docs/                    # methodology, schema, decision memo
├── outputs/                 # scorecards, errors, paired comparisons
├── test_project.py
├── Dockerfile
├── Makefile
└── requirements.txt
```

## Quick start

```bash
git clone https://github.com/sagarmandavkar-UX/llm-evaluation-lab.git
cd llm-evaluation-lab
python -m venv .venv
source .venv/bin/activate
make setup
make analyze
make test
make dashboard
```

## Evaluation protocol

Freeze prompts and rubrics before comparing models. Blind raters to model identity, collect independent labels, adjudicate disagreements, and version every model/prompt/decoding configuration. Define the primary quality metric and severity-specific guardrails before inspecting results.

## Input contract

At minimum: `item_id`, `model`, `domain`, `difficulty`, `rater_1`, `rater_2`, and `error_type`. Optional professional metrics use `confidence`, `latency_ms`, and `cost_usd`.

## Limitations

- The model responses and rater labels are generated, not collected from real models or annotators, so the scores show how the framework works and say nothing about real systems.
- The demo uses binary correctness and one primary error label. Real systems may need ordinal rubrics, refusal quality, factuality grounded in evidence, safety taxonomies, multiple error labels, annotator calibration sessions, and drift monitoring.

## Design choices

- Models are compared with paired inference on common prompts rather than independent aggregate scores.
- Human-label reliability and model confidence calibration are both measured.
- Error analysis feeds a deployment and human-review decision framework.

See [Methodology](docs/METHODOLOGY.md), [Data dictionary](docs/DATA_DICTIONARY.md), and [Executive memo](docs/EXECUTIVE_MEMO.md).

## License

Released under the [MIT License](LICENSE).
