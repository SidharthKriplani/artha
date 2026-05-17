---
title: Fine-Tune Failure Extractor
emoji: 🔍
colorFrom: red
colorTo: yellow
sdk: gradio
sdk_version: 5.9.1
app_file: app.py
pinned: false
short_description: Rank failure modes in your fine-tuned model's eval output.
tags:
  - machine-learning
  - fine-tuning
  - evaluation
  - nlp
  - llm
---

# Fine-Tune Failure Extractor

Stop re-training blindly. Upload your eval output (CSV, JSON, or JSONL) and get a ranked failure mode manifest — which error types your fine-tuned model keeps making, with examples and a training data priority list for your next run.

**7 failure types detected:** wrong operator · off-by-one · missing reasoning step · factual gap · format error · instruction following failure · overconfidence

**Input format:**
```
input,prediction,reference,error_note
"What is 7 × 8?",54,56,wrong operator
"Capital of France?",London,Paris,factual gap
```

**Zero dependencies.** Zero setup. Pure Python.

Built for [artha-ai.sig](https://github.com/SidharthKriplani/artha) — open-source tools built from real developer pain signals.
