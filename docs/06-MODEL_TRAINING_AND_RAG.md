# 🎓 Model Configuration & RAG Strategy

This document describes how each agent is configured (prompts, models, tools) and the RAG strategy for the **Specialist Router Agent**.

---

## Overview

The system uses **pre-trained LLMs** with task-specific prompts rather than fine-tuned models. "Training" here means:

- **Prompt engineering** — designing system and user prompts per agent
- **Model selection** — choosing the right model (and temperature) per task
- **RAG setup** — for the Specialist Router to ground routing decisions in structured knowledge
- **Evaluation & iteration** — improving prompts and retrieval over time

---

## Model Configuration by Agent

| Agent | LLM used? | Primary task | Recommended approach |
|-------|------------|--------------|----------------------|
| **Greeter** | Yes | Intent + entity extraction | Structured output (JSON) for extraction; low temperature |
| **Bouncer** | Optional | Classification | Prefer rule-based; LLM only if classification rules are complex |
| **Specialist Router** | Yes | Routing (RAG-backed) | RAG retrieval + LLM; grounds decisions in departments knowledge base |
| **Specialists** | Yes | Response generation | Domain prompts |
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

## Specialist Router Agent (RAG-backed)

**Tasks:** Map intent → specialist route, using a knowledge base to ground decisions.

**Configuration:**

- **Model:** Capable model for reasoning over retrieved context
- **Temperature:** 0.0–0.3 — consistent routing
- **RAG:** Retrieval over `departments.json` (or `knowledge_base.json`) before routing decision
- **Output:** Single enum: `card | loan | insurance | fraud | premium`

---

## 🧠 RAG Strategy: Specialist Router

### Why RAG for Routing?

A **lightweight RAG layer** is used by the Specialist Router Agent to **ground routing decisions** in a structured knowledge base of banking departments, supported request types, and high-value services.

This approach:

- **Avoids relying purely on free-form LLM reasoning** — routing is informed by explicit department definitions
- **Improves consistency** — same or similar intents map to the same specialist
- **Handles edge cases** — e.g., "yacht insurance" → specialty_insurance via topic match
- **Single, focused RAG point** — simpler than RAG in multiple specialists

---

### Knowledge Base Structure

Keep it simple. Use `departments.json` (or `knowledge_base.json`) with structured documents:

```json
[
  {
    "department": "card_support",
    "topics": ["lost card", "stolen card", "blocked card", "replacement", "PIN reset"],
    "premium_supported": true,
    "description": "Handles debit and credit card operational issues."
  },
  {
    "department": "loan",
    "topics": ["loan application", "mortgage", "credit", "interest rates", "refinancing"],
    "premium_supported": true,
    "description": "Handles loan and mortgage requests."
  },
  {
    "department": "specialty_insurance",
    "topics": ["yacht insurance", "marine insurance", "high-value assets", "boat insurance"],
    "premium_supported": true,
    "description": "Handles specialized insurance requests for high-value assets."
  },
  {
    "department": "fraud",
    "topics": ["suspicious transaction", "dispute", "unauthorized charge", "fraud alert"],
    "premium_supported": true,
    "description": "Handles fraud detection and dispute resolution."
  },
  {
    "department": "premium",
    "topics": ["wealth management", "concierge", "premium services", "VIP"],
    "premium_supported": true,
    "description": "Handles high-value and premium customer services."
  }
]
```

**Fields:**

| Field | Purpose |
|-------|---------|
| `department` | Maps to specialist route |
| `topics` | Keywords/phrases for retrieval (BM25 or embedding match) |
| `premium_supported` | Eligibility for premium customers |
| `description` | Semantic context for embeddings |

---

### Retrieval Options

| Approach | Complexity | When to use |
|----------|-------------|-------------|
| **BM25 / keyword** | Low | Keep it lightweight; small knowledge base |
| **Embeddings + vector store** | Medium | Better semantic match (e.g., "my boat" → yacht) |
| **FAISS / Chroma** | Medium | If you want to impress; scales to larger KB |

**Recommendation:** Start with **BM25 or simple keyword matching** over `topics` and `description`. Add embeddings (e.g., `text-embedding-3-small`) if you need better semantic recall.

---

### RAG Flow for Specialist Router

```
User intent + customer_type
         ↓
    Build query (intent + context)
         ↓
    Retrieve top-K departments (BM25 or vector search)
         ↓
    LLM prompt: retrieved departments + intent + customer_type
         ↓
    specialist_route (grounded in KB)
```

---

### Implementation Notes

- **Location:** `app/agents/specialist_router.py` or `app/services/routing_service.py`
- **Data:** `app/data/departments.json`
- **Retrieval:** `app/services/routing_service.py` — load KB, search, return matched departments
- **Dependencies (if embeddings):** `langchain`, `chromadb` or `faiss-cpu`, embedding model

---

## Specialist Agents

**Tasks:** Domain-specific response generation.

**Configuration:**

- **Model:** Capable model for natural language (e.g., GPT-4o, Claude Sonnet)
- **Temperature:** 0.3–0.5 — natural, varied responses
- **Prompt design:** Role-specific system prompt; conversation context and customer type

**Note:** Specialists do not use RAG. Only the Specialist Router does.

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
| **Router** | **Routing accuracy; RAG recall** | **Expand topics in departments.json; tune retrieval** |
| Specialists | Response quality, relevance | Improve prompts |
| Guardrails | False positives/negatives | Adjust blocklist; refine policy prompts |

---

## Summary

| Agent | Config focus | RAG? |
|-------|--------------|------|
| Greeter | Structured extraction, low temp | No |
| Bouncer | Rule-based preferred | No |
| **Specialist Router** | **RAG-backed routing; departments KB** | **Yes** |
| Specialists | Domain prompts | No |
| Guardrails | Rule-based validation | No |

---

*Back to [Documentation Index](./README.md)*
