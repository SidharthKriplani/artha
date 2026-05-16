# Scope & Compatibility — rag-eval-starter

---

## Who it's for

| Dimension | Detail |
|---|---|
| **Skill level** | Beginner–intermediate. You need to know what RAG is and have an API key. No ML background required. |
| **Role** | Solo builders, AI engineers, anyone evaluating a RAG stack before committing to a model or chunk size. |
| **Use case** | Prototyping and evaluation — not production monitoring. You run this once (or a few times) to understand what actually moves the needle in your RAG pipeline. |
| **Not for** | Teams needing real-time observability, CI/CD eval gates, or evaluation at scale (use Arize Phoenix or Langfuse for those). |

---

## Scale

| Dimension | Comfortable range | Hard limit |
|---|---|---|
| Document size | Up to ~50 pages per file | ~200 pages (memory pressure on FAISS index) |
| Number of documents | 1–5 files per session | Untested above 10 |
| Number of eval questions | 3–20 per run | No hard limit, but RAGAS cost scales with LLM calls |
| Providers per run | Any subset of 4 | All 4 simultaneously is fine |
| Models per run | Any combination | No limit, but runtime grows linearly |

---

## Environment

| Dimension | Status |
|---|---|
| **Mac (Intel + Apple Silicon)** | ✅ Tested |
| **Linux** | ✅ Should work |
| **Windows** | ⚠️ Untested — FAISS may need manual install |
| **HuggingFace Spaces** | ✅ Live — try without installing anything |
| **Python version** | 3.10+ required |
| **GPU** | Not required |
| **Internet** | Required (API calls to providers) |
| **Disk** | ~500MB for sentence-transformers cache (only if no OpenAI key provided) |
| **RAM** | ~2GB comfortable |

**API keys needed:** at least one of OpenAI, Anthropic, Google, or Groq.

---

## What it covers

- Upload your own PDFs and evaluate RAG quality on them
- Compare chunk sizes (256 vs 512 tokens) as an explicit variable
- Mix and match providers and models in one run
- Three RAGAS metrics: faithfulness, answer relevancy, context precision
- Cross-provider verdict: which model/config performed best on your documents
- Fallback embeddings (sentence-transformers) if no OpenAI key — no GPU needed

---

## What it doesn't cover

- **Documents:** images, tables, scanned PDFs, non-English text
- **Retrieval strategies:** only top-k flat FAISS — no hybrid search, no reranking, no MMR
- **Persistence:** no saved sessions, results reset on page reload (HF Spaces) or script exit
- **Production monitoring:** not designed for continuous eval in live systems
- **Custom metrics:** only the three RAGAS metrics — no task-specific scoring
- **Streaming / async:** synchronous only

---

## Known limitations

- RAGAS scores are LLM-as-judge: same config can vary ±5–10% between runs
- Groq free tier rate limits cause failures on large prompt batches
- Anthropic does not provide an embeddings API — falls back to OpenAI or sentence-transformers
- HuggingFace Spaces sessions reset after inactivity — uploaded files are lost
- Very long documents (200+ pages) may silently truncate or cause OOM errors
