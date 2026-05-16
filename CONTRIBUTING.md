# Contributing to ARTHA

ARTHA is an open-source signal intelligence system built on a simple principle:
**every tool here traces back to a real developer pain point with real evidence.**

This is not a repo where you add features because they sound useful.
It is a repo where you build things because you know — from community evidence — that people need them.

If that resonates with you, read on.

---

## Who can contribute

**You write code** → Build a solution for an open signal in [IDEAS.md](IDEAS.md).

**You do research** → Validate a signal, add evidence to an existing one, or document a new pain point in [SIGNALS.md](SIGNALS.md).

**You hit a wall** → Open an issue describing your pain. That is a contribution. Real signals are the raw material of this repo.

**You find a bug** → Fix it and open a PR. Standard stuff.

---

## The philosophy

Most open source contributions fail because the contributor doesn't know whether what they're building matters.

ARTHA solves this differently. Every open idea in [IDEAS.md](IDEAS.md) links to a documented signal — a real community thread with real upvotes and real discussion. Before you write a line of code, you can verify for yourself that the problem is real.

**The optimization objective — read this before proposing anything:**

The bar for a solution is not "does this solve a real problem." The bar is:

> Does a fully-solving, zero-friction version of this already exist for AI/ML builders?

Something always exists. The question is whether it requires accounts, complex setup, deep expertise, or solves a slightly different problem for a different audience. If existing solutions fall short on any of these — there is a real gap worth filling.

Before claiming a signal, spend 10 minutes searching. If you find a tool that fully solves it with zero friction for the target user — the gap is closed. Document what you found in the signal issue and move on to the next one. That is also a contribution.

This means:
- You don't build things nobody asked for
- You don't compete with existing tools that already solve the problem
- Your contribution is traceable to evidence, not guesswork

---

## How to build a solution

### 1. Find an open idea

Read [IDEAS.md](IDEAS.md). Find something that matches your skills and interests.
Read the linked signal in [SIGNALS.md](SIGNALS.md) — understand the pain before writing code.

### 2. Claim it

Run this from the repo root:
```bash
python3 track.py --claim SIGNAL-XXX --github your-github-username
```

This marks the signal as claimed so no one else starts the same thing in parallel.

### 3. Build it

Each solution lives in `solutions/your-solution-name/`.

Every solution must include:
- `README.md` — what it does, how to use it, the signal it traces to
- `problem.md` — the pain, who has it, why existing tools don't solve it
- Working code with a clear entry point (CLI or Gradio app preferred)
- `requirements.txt`

Optionally (but strongly encouraged):
- `prd.md` — what's in scope, what's deliberately excluded
- `eval_plan.md` — how you know it works
- `CONTEXT.md` — technical decisions and tradeoffs

### 4. Open a PR

Title: `[SOLUTION] Your solution name — SIGNAL-XXX`

In the PR description, link to the signal and explain one key technical decision you made.

### 5. Get credited

Once merged, you appear in [CONTRIBUTORS.md](CONTRIBUTORS.md) with your name, what you built, and which signal it traces to. Permanently.

---

## How to add a signal

If you've hit a pain point that isn't in [SIGNALS.md](SIGNALS.md):

1. Open an issue titled: `[SIGNAL] Your pain in one sentence`
2. In the body, describe:
   - What you were trying to do
   - What broke or was missing
   - What you tried (workarounds, existing tools)
   - Links to Reddit / HN / GitHub issues where others describe the same thing
3. If the signal is real, specific, and has evidence — it gets added

**Signals without community evidence don't get added.** This is not about ideas. It is about documented problems.

---

## How to improve an existing solution

Every solution has an `IDEAS.md` file with specific, scoped improvement ideas. Pick one, open a PR.

For `rag-eval-starter`, see [solutions/rag-eval-starter/IDEAS.md](solutions/rag-eval-starter/IDEAS.md).

---

## Standards

- Code should run in one command from a clean install
- No unnecessary dependencies
- If you use an LLM, document why and what it costs
- If your solution has known limitations, document them honestly

---

## Questions

Open an issue. That's it.
