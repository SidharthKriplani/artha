# Problem — rag-eval-starter

## Signal source

**Thread:** [r/LocalLLaMA — "Evaluated a RAG chatbot and the most expensive model was the worst performer"](https://www.reddit.com/r/LocalLLaMA/comments/1tdusvx/)
**Signal strength:** 22↑ · 27💬 · score 2

## The pain

Builders switch to expensive models (gpt-4o, Claude Opus) when RAG quality is poor, assuming cost equals quality. The thread documents a real production case: a customer support RAG bot where the most expensive model scored worst. The actual performance drivers were chunk size and retrieval strategy — not the model.

The problem is not that this is unknown in principle. The problem is that no one measures it before spending. There is no standard, zero-friction tool that makes the comparison visible on your own documents with your own questions.

## What already exists — honest assessment

**RAGAS** — the evaluation framework this tool is built on. RAGAS has a quickstart CLI and multiple public notebooks. The gap: RAGAS is single-provider by default and treats retrieval parameters as fixed, not as variables to compare. It is an evaluation library, not a comparison tool.

**Existing notebooks** (Pinecone, NVIDIA AI Blueprints, community examples) — functional but single-provider, require infra setup, and are designed as tutorials not reusable comparison tools.

**Arize Phoenix** — excellent open-source observability platform, self-hosted, no account. The gap: observability-first — you instrument an existing pipeline and monitor it. Not designed to sweep configurations and compare them side-by-side.

**LangSmith, DeepEval** — require accounts, designed for production monitoring not configuration comparison experiments.

## The specific gap this tool fills

No existing tool does all three together with zero infrastructure:

1. **Multi-provider comparison** — OpenAI vs Anthropic vs Gemini vs Groq in a single run
2. **Retrieval parameters as the primary variable** — chunk size and top-k are the explicit comparison axes, not afterthoughts
3. **Zero-friction deployment** — Gradio UI on HuggingFace Spaces, no server, no database, no account

The differentiator is narrow but real: this is the only tool that makes multi-provider RAG config comparison runnable in a browser with no setup.

## Who has this pain

AI/ML builders running RAG pipelines — most active in r/LocalLLaMA and r/LanguageModelHacking. Solo builders and small teams without dedicated ML infrastructure.

## Why existing workarounds fall short

The most common workaround is switching models when quality is poor and hoping it improves. This is expensive and usually wrong — the bottleneck is retrieval, not generation. The second workaround is writing a custom eval notebook — which requires writing evaluation code, setting up a vector store, and handling multi-provider API differences manually. This tool removes all of that.

## Success criteria

- A builder runs a multi-provider RAG eval on their own documents in under 5 minutes with no setup beyond an API key
- The output makes clear whether switching models or changing retrieval config is the higher-leverage intervention
- At least one person who hit the original pain point finds it useful
