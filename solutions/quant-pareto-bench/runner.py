"""
Model runner: loads a GGUF file via llama-cpp-python, runs prompts, records
latency and token throughput. Returns structured BenchResult objects.
"""

import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PromptResult:
    prompt: str
    output: str
    prompt_tokens: int
    output_tokens: int
    time_to_first_token_ms: float   # estimated from total / output_tokens
    total_latency_ms: float
    tokens_per_second: float


@dataclass
class BenchResult:
    model_path: str
    quant_label: str        # e.g. "Q4_K_M", "Q8_0", "F16"
    prompt_results: list[PromptResult]

    @property
    def avg_tokens_per_second(self) -> float:
        if not self.prompt_results:
            return 0.0
        return sum(r.tokens_per_second for r in self.prompt_results) / len(self.prompt_results)

    @property
    def avg_latency_ms(self) -> float:
        if not self.prompt_results:
            return 0.0
        return sum(r.total_latency_ms for r in self.prompt_results) / len(self.prompt_results)


def _infer_quant_label(model_path: str) -> str:
    """Extract quant level from GGUF filename heuristically."""
    name = Path(model_path).stem.upper()
    for candidate in ["Q2_K", "Q3_K_S", "Q3_K_M", "Q3_K_L", "Q4_0", "Q4_K_S",
                      "Q4_K_M", "Q5_0", "Q5_K_S", "Q5_K_M", "Q6_K", "Q8_0", "F16", "F32"]:
        if candidate in name:
            return candidate
    return Path(model_path).stem


def run_model(
    model_path: str,
    prompts: list[str],
    n_ctx: int = 2048,
    max_tokens: int = 256,
    temperature: float = 0.0,
    n_gpu_layers: int = 0,
    verbose: bool = False,
) -> BenchResult:
    """
    Load a GGUF model and run all prompts through it.
    Returns a BenchResult with per-prompt latency and throughput.
    """
    try:
        from llama_cpp import Llama
    except ImportError:
        raise ImportError(
            "llama-cpp-python is required.\n"
            "Install: pip install llama-cpp-python\n"
            "For Metal (Apple Silicon): CMAKE_ARGS='-DLLAMA_METAL=on' pip install llama-cpp-python"
        )

    quant_label = _infer_quant_label(model_path)

    llm = Llama(
        model_path=model_path,
        n_ctx=n_ctx,
        n_gpu_layers=n_gpu_layers,
        verbose=verbose,
    )

    results = []
    for prompt in prompts:
        t0 = time.perf_counter()
        response = llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            echo=False,
        )
        t1 = time.perf_counter()

        total_ms = (t1 - t0) * 1000
        output_text = response["choices"][0]["text"].strip()
        usage = response.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 1)

        tps = completion_tokens / (total_ms / 1000) if total_ms > 0 else 0.0
        # approximate ttft: assume prompt eval is ~30% of total for first call
        ttft = total_ms * 0.3

        results.append(PromptResult(
            prompt=prompt,
            output=output_text,
            prompt_tokens=prompt_tokens,
            output_tokens=completion_tokens,
            time_to_first_token_ms=ttft,
            total_latency_ms=total_ms,
            tokens_per_second=tps,
        ))

    del llm  # free memory before loading next model
    return BenchResult(
        model_path=model_path,
        quant_label=quant_label,
        prompt_results=results,
    )
