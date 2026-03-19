# 🔍 Observability with LangSmith

LangSmith provides tracing and observability for the multi-agent workflow.

---

## Setup

1. **Sign up** at [smith.langchain.com](https://smith.langchain.com) (free tier available).

2. **Create an API key** in Settings → API Keys.

3. **Add to `.env`**:
   ```
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=lsv2_pt_...
   ```

4. **Run the app** — traces will appear automatically in LangSmith.

---

## What Gets Traced

| Component | Traced? |
|-----------|---------|
| **LangGraph workflow** | Yes — graph execution, node transitions |
| **Extraction (ChatOpenAI)** | Yes — intent and identification LLM calls |
| **Verification** | No — deterministic logic (no LLM) |

---

## Viewing Traces

- Go to [smith.langchain.com](https://smith.langchain.com) → Traces
- Each `/chat` request creates a trace
- Expand to see: graph nodes, LLM inputs/outputs, latency

---

## Disabling Tracing

Remove or set in `.env`:
```
LANGCHAIN_TRACING_V2=false
```

Or omit `LANGCHAIN_API_KEY` — tracing will be disabled.

---

*Back to [Documentation Index](./README.md)*
