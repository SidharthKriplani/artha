# Eval Plan: Does This Solution Actually Work?

## How We Know This Notebook Is Useful

### Metric 1 — It runs without errors on a clean install
Someone with Python + pip should get to a results table in under 30 minutes.
Pass condition: zero code changes required for the sample dataset path.

### Metric 2 — Scores differ meaningfully across configurations
If all configurations score within 0.02 of each other, the eval is not discriminating.
Pass condition: at least one configuration scores >0.1 higher than another on at least one metric.

### Metric 3 — The worst configuration is identifiable
The notebook should clearly surface which setup underperforms, not just which one wins.
Pass condition: results table sortable by metric, with a clear bottom performer.

### Metric 4 — External validation
Post in the thread that inspired this. If at least 2 people say it solved their problem or star the repo, the signal was real.

---

## What We Are Not Evaluating

- Speed of the notebook (not a production tool)
- Cost of API calls (users control their own keys)
- Accuracy of RAGAS metrics themselves (known limitation — documented in CONTEXT.md)
