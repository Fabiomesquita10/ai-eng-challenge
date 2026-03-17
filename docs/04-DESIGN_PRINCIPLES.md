# ⚙️ Design Principles

This document outlines the core design principles that guide the architecture and implementation of the multi-agent banking support system.

---

## 1. Separation of Concerns

**Each agent has a clear, single responsibility.**

- Greeter: identification and intent
- Bouncer: classification
- Specialist Router: routing
- Specialists: domain handling
- Guardrails: safety and compliance

This makes the system easier to understand, test, and maintain. Changes to one agent do not require changes to others.

---

## 2. State-Driven Orchestration

**Agents communicate through shared state, not by calling each other.**

- No direct agent-to-agent calls
- The orchestration layer (LangGraph) controls flow based on state
- Each agent reads from and writes to a common `ConversationState`

**Benefits:**

- Clear data flow
- Easy to add logging and observability
- Deterministic routing logic
- Testable in isolation

---

## 3. Deterministic Core Logic

**Critical logic does not rely on LLMs.**

The following are implemented with **rule-based, deterministic logic**:

| Logic | Why deterministic? |
|-------|--------------------|
| Identity verification (2/3 rule) | Must be consistent and correct; no room for hallucination |
| Customer classification | Business rules must be applied uniformly |
| Routing decisions | Predictable behavior for debugging and compliance |
| Policy enforcement | Guardrails must reliably block unsafe behavior |

LLMs introduce variability. For business-critical decisions, deterministic logic is preferred.

---

## 4. Selective Use of LLMs

**LLMs are used only where they add value.**

| Use case | LLM? | Reason |
|----------|------|--------|
| Intent extraction | Yes | Natural language is ambiguous; LLMs handle variation well |
| Entity extraction (name, phone, IBAN) | Yes | Flexible parsing of user messages |
| Response generation | Yes | Natural, contextual replies |
| Identity verification | No | Rule-based (2/3 match) |
| Customer classification | No | Rule-based (eligibility rules) |
| Routing | No | Rule-based (intent → domain mapping) |

This hybrid approach ensures:

- **Flexibility** where AI helps (interpretation, NLG)
- **Reliability** where rules matter (verification, routing, compliance)

---

## 5. RAG Where It Adds Value

**RAG is used only where retrieval genuinely improves the solution.**

- **Routing:** Rule-first + prompt engineering suffice. RAG for routing would feel forced.
- **Insurance Specialist:** RAG grounds responses in product docs, specialty coverage, routing policies. Here retrieval adds real value — more informed, credible responses.

This shows maturity: not everything needs RAG; use it where it matters.

---

## 6. Extensibility

**New agents or specialists can be added easily.**

- Add a new specialist: add a node, update routing logic
- Add a new customer type: extend Bouncer rules
- Add a new intent: extend Specialist Router mapping

The architecture does not require refactoring existing agents when extending the system.

---

## 7. Testability

**Key logic is unit-testable.**

- Verification service: test 2/3 rule with various inputs
- Routing service: test intent → specialist mapping
- Guardrails: test policy enforcement

Integration tests can exercise full flows without relying on LLM calls (using mocks or deterministic fixtures).

---

## Summary

| Principle | Implementation |
|-----------|----------------|
| Separation of concerns | One agent, one responsibility |
| State-driven orchestration | Shared state; LangGraph controls flow |
| Deterministic core logic | Rules for verification, classification, routing |
| Selective LLM use | LLMs for extraction and generation; rules for decisions |
| RAG where it adds value | Insurance Specialist only; not for routing |
| Extensibility | Modular agents; easy to add specialists |
| Testability | Unit tests for services; mock LLMs in integration tests |

---

*Next: [05 - Why LangGraph](./05-WHY_LANGGRAPH.md)*
