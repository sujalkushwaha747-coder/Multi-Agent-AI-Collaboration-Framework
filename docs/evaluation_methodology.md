# Evaluation Methodology

ShodhAI uses transparent scoring logic and labels estimated metrics. It avoids presenting estimated values as objective ground truth.

## Accuracy

When a reference answer is supplied, accuracy is calculated with token-level F1 overlap between the generated response and the reference answer.

When retrieved evidence is available, accuracy is calculated against the retrieved context.

When neither reference answer nor evidence exists, the score is labeled estimated and derived from response quality and coverage signals.

## Response Quality

Response quality is estimated from:

- length adequacy
- organization
- sentence clarity
- lexical usefulness

The score is 0-100.

## Hallucination Rate

When evidence exists, ShodhAI estimates unsupported claims by checking whether substantive response sentences have low overlap with retrieved evidence.

When no evidence exists, ShodhAI labels the score as estimated hallucination risk.

Lower is better.

## Completeness

Completeness estimates how many important prompt terms and requirements are addressed by the response.

## Execution Time

Execution time is measured with backend wall-clock timing. Single-Agent and Multi-Agent durations are stored separately.

## Overall Score

The overall score uses normalized metric direction:

- Accuracy benefit = accuracy / 100
- Quality benefit = quality / 100
- Completeness benefit = completeness / 100
- Hallucination benefit = 1 - hallucination rate / 100
- Speed benefit = inverse normalized execution time

Default weights:

- Accuracy: 25%
- Quality: 25%
- Completeness: 20%
- Hallucination: 20%
- Execution Time: 10%

These weights are configurable and are not a universal scientific standard.

