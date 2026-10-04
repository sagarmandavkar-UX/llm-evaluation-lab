# Executive memo

## Decision question

Which candidate model provides the best quality–cost–latency tradeoff for the evaluated workload, and where is human review still required?

## Demonstration finding

The synthetic `reasoning` model leads aggregate accuracy, while smaller models remain cheaper and faster. The error taxonomy and domain/difficulty scorecard show why a single overall percentage is insufficient.

## Recommendation

Select the production candidate using a predeclared quality floor and operational budget. Route high-severity or poorly performing slices to human review, and rerun the versioned benchmark whenever the model, prompt, retrieval layer, or policy changes.
