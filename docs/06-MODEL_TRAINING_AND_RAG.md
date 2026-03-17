# 🎓 Model Configuration & RAG Strategy

This document describes how each agent is configured (prompts, models, tools) and the RAG strategy for the **Insurance Specialist Agent**.

---

## Overview

The system uses **pre-trained LLMs** with task-specific prompts rather than fine-tuned models. "Training" here means:

- **Prompt engineering** — designing system and user prompts per agent
- **Model selection** — choosing the right model (and temperature) per task
- **RAG setup** — for the Insurance Specialist to ground responses in insurance documentation
- **Evaluation & iteration** — improving prompts and retrieval over time

---

## Model Configuration by Agent

| Agent | LLM used? | Primary task | Recommended approach |
|-------|------------|--------------|----------------------|
| **Greeter** | Yes | Intent + entity extraction | Structured output (JSON) for extraction; low temperature |
| **Bouncer** | Optional | Classification | Prefer rule-based; LLM only if classification rules are complex |
| **Specialist Router** | Optional | Routing | Rule-first + prompt engineering + few-shot examples; LLM fallback for ambiguous intents |
| **Specialists** | Yes | Response generation | Domain prompts; **Insurance uses RAG** |
| **Guardrails** | Optional | Validation | Rule-based + optional LLM for content safety |

---

## Greeter Agent

**Tasks:** Intent extraction, entity extraction (name, phone, IBAN), merge with session.

**Configuration:**

- **Model:** Fast, cost-effective model (e.g., GPT-4o-mini, Claude Haiku)
- **Temperature:** 0.0–0.2 — deterministic, structured output
- **Output format:** JSON schema for `intent`, `name`, `phone`, `iban`
- **Prompt design:** Extraction rules, 2/3 verification context, few-shot examples

---

## Bouncer Agent

**Tasks:** Customer classification (regular, premium, not a customer).

**Configuration:**

- **Model:** Optional — can be fully rule-based using `customer_service` + account data
- **Recommendation:** Keep rule-based for consistency and predictability

---

## Specialist Router Agent

**Tasks:** Map intent → specialist route.

**Configuration:**

- **Model:** Optional — rule-first with LLM fallback for ambiguous cases
- **Approach:** Rules + prompt engineering + few-shot examples. **No RAG** — with a handful of well-defined routes, retrieval would feel forced.
- **Inputs:** `intent`, `customer_type`, `high_value` flag
- **Output:** Single enum: `card | loan | insurance | fraud | premium`

**Routing config:** `departments.json` — used for rule-based keyword/topic matching, not vector retrieval.

---

## Specialist Agents

**Tasks:** Domain-specific response generation.

**Configuration:**

- **Model:** Capable model for natural language (e.g., GPT-4o, Claude Sonnet)
- **Temperature:** 0.3–0.5 — natural, varied responses
- **Prompt design:** Role-specific system prompt; conversation context and customer type

**Special case:** Insurance Specialist uses **RAG** (see below).

---

## 🧠 RAG Strategy: Insurance Specialist

### Why RAG for Insurance (and not for Routing)?

**Routing** with a handful of well-defined routes is better solved with:

- Rules
- Prompt engineering
- Few-shot examples
- Rule-first + LLM fallback

Using RAG for routing can feel like "I used it just because."

**Insurance Specialist** is different. Here you're not just deciding where to route — you're **giving a more informed response** based on specific knowledge. RAG adds real value:

- User asks something specific (e.g., "yacht insurance policy")
- Router sends to Insurance Specialist
- Insurance Specialist **retrieves** from a knowledge base
- Response is **grounded** in actual documentation

This demonstrates retrieval-augmented reasoning where it genuinely improves the solution.

---

### README Pitch

> A lightweight RAG component is used inside the Insurance Specialist Agent to ground responses on a small internal knowledge base of insurance products, specialty coverage areas, and routing policies. This demonstrates retrieval-augmented reasoning where it adds real value, rather than using retrieval for simple routing decisions.

---

### Example Flow

**User:** "I need help with my yacht insurance policy"

1. Greeter → identifies customer
2. Bouncer → premium
3. Specialist Router → `insurance_specialist_agent` (no RAG)
4. **Insurance Specialist:**
   - Retrieves from insurance KB
   - Finds docs on: marine insurance, high-value asset insurance, specialty insurance handling
   - Responds: *"This request falls under our specialty insurance support team. Our marine and high-value asset coverage team handles yacht insurance policies. I'll connect you with the appropriate specialist..."*

---

### Knowledge Base Structure

Keep it simple. A small set of markdown files:

| File | Content |
|------|---------|
| `insurance_products.md` | Supported insurance types, product overview |
| `specialty_insurance.md` | Marine, yacht, high-value assets, specialty coverage |
| `premium_insurance_routing.md` | Premium escalation, teams responsible, routing policies |

**Location:** `app/data/insurance/`

**Content examples:**

- Types of insurance supported (car, home, marine, specialty)
- Specialty requests (yacht, boat, high-value assets)
- Responsible teams and escalation paths
- Premium customer handling

---

### RAG Flow for Insurance Specialist

```
User query + conversation context
         ↓
    Build query (intent / subcategory)
         ↓
    Retrieve top-K chunks (embeddings or BM25)
         ↓
    LLM prompt: retrieved chunks + query + context
         ↓
    Response (grounded in docs)
```

---

### Retrieval Options

| Approach | Complexity | When to use |
|----------|-------------|-------------|
| **BM25 / keyword** | Low | Small KB; simple matching |
| **Embeddings + vector store** | Medium | Better semantic match ("my boat" → yacht) |
| **FAISS / Chroma** | Medium | If you want to impress; scales |

**Recommendation:** Start with embeddings + simple vector store. The KB is small; no need to overcomplicate.

---

### Implementation Notes

- **Location:** `app/agents/specialists/insurance.py` — uses RAG before generating response
- **Service:** `app/services/insurance_rag_service.py` — load docs, chunk, embed, search
- **Data:** `app/data/insurance/*.md`
- **Dependencies:** `langchain`, `chromadb` or `faiss-cpu`, embedding model

---

## Guardrails

**Tasks:** Input/output validation, policy enforcement.

**Configuration:**

- **Model:** Optional — rule-based validation preferred
- **Recommendation:** Rule-based first; add LLM only if needed for complex cases

---

## Evaluation & Iteration

| Agent | What to measure | How to improve |
|-------|-----------------|----------------|
| Greeter | Extraction accuracy (intent, entities) | Add few-shot examples; refine schema |
| Bouncer | Classification accuracy | Tighten rules; add edge cases |
| Router | Routing accuracy | Expand rules; add few-shot examples |
| **Insurance Specialist** | **Response quality; RAG recall** | **Add docs to KB; tune retrieval; improve prompts** |
| Other Specialists | Response quality | Improve prompts |
| Guardrails | False positives/negatives | Adjust blocklist; refine policy prompts |

---

## Summary

| Agent | Config focus | RAG? |
|-------|--------------|------|
| Greeter | Structured extraction, low temp | No |
| Bouncer | Rule-based preferred | No |
| Specialist Router | Rule-first + prompt + LLM fallback | No |
| Card, Loan, Fraud, Premium | Domain prompts | No |
| **Insurance Specialist** | **Domain prompts + RAG** | **Yes** |
| Guardrails | Rule-based validation | No |

---

## Design Maturity

This architecture shows **maturity**:

- Not everything needs RAG
- Not everything needs embeddings
- RAG is used where it **genuinely improves** the solution
- Better than spreading RAG across the system just to impress

---

*Back to [Documentation Index](./README.md)*
