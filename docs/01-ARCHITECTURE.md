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
Greeter Agent (Identification & Intent)
     ↓
Bouncer Agent (Customer Classification)
     ↓
Specialist Router Agent
   └─ RAG Retrieval over departments / services knowledge base
     ↓
Specialist Agent (Domain Handling)
     ↓
Guardrails (Safety & Compliance)
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
| **Specialist Router** | Maps intent to domain; uses RAG over departments knowledge base to ground routing decisions; selects the correct specialist |
| **Specialist Agent** | Handles domain-specific logic (card, loan, insurance, fraud, premium) |
| **Guardrails** | Validates input/output; enforces policies; prevents unsafe behavior |

---

## Data Flow

1. **User** sends a message via the `/chat` endpoint.
2. **Session Manager** loads or creates a session; merges with conversation history.
3. **Greeter** extracts intent and identification fields; verifies using the 2-out-of-3 rule.
4. **Bouncer** determines customer type and eligibility.
5. **Specialist Router** retrieves relevant department/service info via RAG, then selects the appropriate specialist based on intent, customer type, and retrieved knowledge.
6. **Specialist** processes the request and generates a domain-specific response.
7. **Guardrails** validate the response before it is returned.
8. **Session Manager** saves the updated state.
9. **Response** is returned to the user.

---

## Key Architectural Decisions

- **State-driven orchestration:** All routing is based on shared state, not direct agent-to-agent calls.
- **Deterministic core logic:** Verification, classification, and routing use rule-based logic where possible.
- **Selective LLM use:** LLMs are used for interpretation and natural language generation, not for critical business logic.
- **RAG for routing:** A lightweight RAG layer grounds the Specialist Router's decisions in a structured knowledge base of banking departments and supported request types.
- **Layered design:** Each layer has a single, well-defined responsibility.

---

*Next: [02 - Orchestration Workflow](./02-WORKFLOW.md)*
