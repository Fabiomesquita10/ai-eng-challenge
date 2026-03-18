# 🧠 System Architecture

## Overview

The system follows a **multi-agent architecture**, where each agent is responsible for a specific part of the customer support workflow. Agents do not call each other directly; instead, they communicate through a **shared conversation state** managed by the orchestration layer.

---

## High-Level Flow

```
User Request
     ↓
FastAPI API (/chat)
     ↓
Session Manager (Memory)
     ↓
Input Guardrails (right after user message — block dangerous requests)
     ↓
Greeter Agent (Identification & Intent)
     ↓
Bouncer Agent (Customer Classification)
     ↓
Specialist Router Agent (rules + prompt + LLM fallback)
     ↓
Specialist Agent (Domain Handling)
   └─ Insurance Specialist: RAG over insurance knowledge base
     ↓
Output Guardrails (before any response — redact, validate, safe rewrite)
     ↓
Response
```

---

## Component Responsibilities

| Component | Responsibility |
|-----------|----------------|
| **FastAPI API** | Entry point; receives chat requests, delegates to orchestration |
| **Session Manager** | Persists conversation history; enables multi-turn context |
| **Greeter Agent** | Extracts intent and identification data; verifies customer legitimacy |
| **Bouncer Agent** | Classifies customer type (regular, premium, not a customer) |
| **Specialist Router** | Maps intent to domain; rule-first + LLM fallback; selects the correct specialist |
| **Specialist Agent** | Handles domain-specific logic; **Insurance Specialist** uses RAG over insurance knowledge base for grounded responses |
| **Input Guardrails** | Validates user message right after load; blocks dangerous requests |
| **Output Guardrails** | Validates response before return; redacts sensitive data; safe rewrite |

---

## Data Flow

1. **User** sends a message via the `/chat` endpoint.
2. **Session Manager** loads or creates a session; merges with conversation history.
3. **Input Guardrails** validate the user message; block dangerous requests (or pass through).
4. **Greeter** extracts intent and identification fields; verifies using the 2-out-of-3 rule.
5. **Bouncer** determines customer type and eligibility.
6. **Specialist Router** selects the appropriate specialist based on intent, customer type, and high-value flag (rules + prompt engineering + LLM fallback).
7. **Specialist** processes the request; **Insurance Specialist** uses RAG to retrieve relevant docs and generate grounded responses.
8. **Output Guardrails** validate the response (redact, LLM check, safe rewrite) before it is returned.
9. **Session Manager** saves the updated state.
10. **Response** is returned to the user.

---

## Key Architectural Decisions

- **State-driven orchestration:** All routing is based on shared state, not direct agent-to-agent calls.
- **Deterministic core logic:** Verification, classification, and routing use rule-based logic where possible.
- **Selective LLM use:** LLMs are used for interpretation and natural language generation, not for critical business logic.
- **RAG where it adds value:** A lightweight RAG component is used inside the Insurance Specialist to ground responses on an internal knowledge base of insurance products, specialty coverage, and routing policies — rather than using retrieval for simple routing decisions.
- **Layered design:** Each layer has a single, well-defined responsibility.

---

*Next: [02 - Orchestration Workflow](./02-WORKFLOW.md)*
