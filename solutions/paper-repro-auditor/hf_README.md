---
title: Paper Reproduction Gap Auditor
emoji: 📄
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 5.9.1
app_file: app.py
pinned: false
short_description: Stuck below a paper's reported accuracy? Find out why.
tags:
  - machine-learning
  - reproducibility
  - evaluation
  - research
  - nlp
---

# Paper Reproduction Gap Auditor

Stuck below a paper's reported accuracy? Fill in the paper's config and yours across 10 risk dimensions. Get a ranked list of what's most likely causing the gap — sorted HIGH to LOW.

**10 dimensions checked:** random seed · data splits · normalization · metric computation · augmentation · checkpoint selection · optimizer + LR schedule · batch size · training duration · hardware/library versions

**Zero dependencies.** Zero setup. Pure Python.

Built for [artha-ai.sig](https://github.com/SidharthKriplani/artha) — open-source tools built from real developer pain signals.
