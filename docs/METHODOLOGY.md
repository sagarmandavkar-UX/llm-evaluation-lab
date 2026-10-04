# Evaluation methodology

## Evaluation unit

One row represents one model response to one prompt, with a blinded correctness judgment, error category, confidence, observed latency, and estimated cost. Every compared model should answer the same prompt set.

## Primary metrics

- Accuracy with non-parametric bootstrap 95% confidence intervals.
- Paired accuracy differences on the common item set.
- Cohen's kappa for inter-rater agreement.
- Brier score for confidence calibration.
- Median latency and cost per correct response.
- Accuracy slices by domain and difficulty.

## Labeling protocol

1. Freeze the prompt set and rubric before scoring.
2. Blind raters to model identity.
3. Collect two independent labels for a validation sample.
4. Adjudicate disagreements and document rubric revisions.
5. Version model, prompt, decoding parameters, and evaluation date.

## Deployment gate

Choose a primary quality metric and minimum acceptable threshold before comparing models. Add safety-specific failure categories and guardrails for the target use case. A statistically better aggregate score does not override unacceptable failures in high-severity slices.
