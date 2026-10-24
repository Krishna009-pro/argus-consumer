"""Optional vendor-neutral LLM adapter. Credentials are read only at runtime."""
import json, os, time
from pathlib import Path
from urllib.request import Request, urlopen
from .config import load_local_env

class LLMConfigurationError(RuntimeError): pass

def complete(prompt: str, model_tier: str = "research", *, provider: str | None = None) -> str:
    load_local_env()
    provider = provider or os.getenv("ARGUS_LLM_PROVIDER", "openai-compatible")
    provider_key = provider.casefold()
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "ARGUS/1.0 (Autonomous Financial Discovery Engine)",
        "HTTP-Referer": "https://github.com/Krishna009-pro/argus-consumer",
        "X-Title": "ARGUS Financial Forensics",
    }
    if provider_key == "openrouter":
        base = "https://openrouter.ai/api/v1"
        key = os.getenv("OPENROUTER_API_KEY")
    elif provider_key == "groq":
        base = "https://api.groq.com/openai/v1"
        key = os.getenv("GROQ_API_KEY")
    else:
        base = os.getenv("ARGUS_LLM_BASE_URL")
        key = os.getenv("ARGUS_LLM_API_KEY")
    model = os.getenv("ARGUS_LLM_MODEL") or ("openrouter/auto" if provider_key == "openrouter" else None)
    if not base or not key or not model:
        if provider_key in {"openrouter", "groq"}:
            required_key = "OPENROUTER_API_KEY" if provider_key == "openrouter" else "GROQ_API_KEY"
            raise LLMConfigurationError(f"Optional {provider} LLM is not configured. Set {required_key} and ARGUS_LLM_MODEL; deterministic offline analysis remains available.")
        raise LLMConfigurationError("Optional LLM is not configured. Set ARGUS_LLM_BASE_URL, ARGUS_LLM_API_KEY and ARGUS_LLM_MODEL; deterministic offline analysis remains available.")
    endpoint = base.rstrip("/") + "/chat/completions"
    headers["Authorization"] = f"Bearer {key}"
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}], "metadata": {"tier": model_tier}}).encode("utf-8")
    request = Request(endpoint, data=body, headers=headers)
    started = time.perf_counter()
    with urlopen(request, timeout=60) as response:
        payload = json.loads(response.read().decode("utf-8"))
    elapsed = time.perf_counter() - started
    usage = payload.get("usage", {})
    cost = usage.get("cost_usd")
    log = {"provider": provider, "model": model, "tier": model_tier, "input_tokens": usage.get("prompt_tokens"), "output_tokens": usage.get("completion_tokens"), "cost_usd": cost, "elapsed_seconds": elapsed}
    Path("logs").mkdir(exist_ok=True)
    with Path("logs/usage.jsonl").open("a", encoding="utf-8") as f: f.write(json.dumps(log) + "\n")
    return payload["choices"][0]["message"]["content"]
