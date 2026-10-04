# Data dictionary

| Field | Definition |
|---|---|
| `item_id` | Stable identifier for one evaluation prompt |
| `model` | Versioned model or system label |
| `domain` | Subject-matter slice |
| `difficulty` | Predefined difficulty band |
| `rater_1`, `rater_2` | Binary correctness labels from independent raters |
| `error_type` | Primary failure category or `none` |
| `confidence` | Model/system probability assigned to correctness |
| `latency_ms` | End-to-end response latency |
| `cost_usd` | Estimated inference cost per response |

The bundled model labels and observations are synthetic. They demonstrate an evaluation design and do not rank real commercial models.
