# Problem: RAG Evaluation is Expensive, Confusing, and Often Wrong

## Pain Signal

**Source:** r/LocalLLaMA  
**Post:** "Evaluated a RAG chatbot and the most expensive model was the worst performer. Notes on what actually moved the needle"  
**Upvotes:** 22 | **Comments:** 27  
**Signal score:** 2/3

**Supporting signal:** r/MachineLearning  
**Post:** "Production AI very different from the demos"  
**Upvotes:** 15 | **Comments:** 28

---

## What People Are Actually Complaining About

Builders pick expensive frontier models assuming cost correlates with RAG performance. It frequently does not. The real performance drivers — chunk size, retrieval strategy, context construction — are invisible to people who jump straight to model comparison.

The comments on the source thread reveal a consistent pattern:
- People are running informal, ad-hoc evaluations with no reproducible structure
- Switching models without changing anything else and drawing wrong conclusions
- No baseline established before experimenting
- Evaluation metrics either missing entirely or reduced to "does it sound right"

---

## Who Has This Problem

**Primary:** Indie builders and early-stage startup engineers building RAG-based products (chatbots, document QA, support agents). They have a working demo but cannot tell why it performs inconsistently in production.

**Secondary:** ML engineers at companies piloting internal RAG tools who need to justify model/infra choices to non-technical stakeholders.

---

## Why Existing Solutions Do Not Fully Solve It

- **RAGAS** is powerful but has a steep setup curve — most builders bounce before getting a single eval run working
- **DeepEval** requires account setup and is oriented toward teams, not solo builders
- **LangSmith** is observability-first, not evaluation-first
- **OpenAI evals** framework is too generic and not RAG-specific

The gap: there is no minimal, copy-paste-ready evaluation harness that a solo builder can run in one notebook with their own data in under 30 minutes.

---

## What Success Looks Like

A builder clones this repo, drops in their own documents and questions, runs one notebook, and gets a structured report showing which retrieval + model combination performs best on their specific data — with metrics they can explain to a non-technical stakeholder.
