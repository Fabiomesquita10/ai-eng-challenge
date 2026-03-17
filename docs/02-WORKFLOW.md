# 🔁 Orchestration Flow

This document describes the **LangGraph workflow** — the execution flow and routing logic that governs how agents interact.

---

## Workflow Diagram

```
START
  │
  ▼
load_session
  │
  ▼
input_guardrails (right after user message)
  │
  ├── input blocked ────────► save_session ──► END
  │
  └── OK ───────────────────► greeter_agent
                                │
                                ├── needs_more_info ──────► output_guardrails ──► save_session ──► END
                                │
                                ├── identification_failed ─► output_guardrails ──► save_session ──► END
                                │
                                └── is_identified ────────► bouncer_agent
                                                              │
                                                              ▼
                                                         specialist_router_agent
                                                              │   (rules + prompt + LLM fallback)
                                                              │
                                                              ├── card ──────► card_specialist
                                                              ├── loan ──────► loan_specialist
                                                              ├── insurance ─► insurance_specialist (RAG)
                                                              ├── fraud ─────► fraud_specialist
                                                              └── premium ───► premium_specialist
                                                                                │
                                                                                ▼
                                                                           output_guardrails
                                                                                │
                                                                                ▼
                                                                           save_session
                                                                                │
                                                                                ▼
                                                                               END
```

---

## State Transitions

| From | Condition | To |
|------|-----------|-----|
| load_session | (always) | input_guardrails |
| input_guardrails | `guardrail_flagged == True` | save_session → End |
| input_guardrails | OK | Greeter |
| Greeter | `needs_more_info == True` | output_guardrails → End |
| Greeter | `identification_failed == True` | output_guardrails → End |
| Greeter | `is_identified == True` | Bouncer |
| Bouncer | (always) | Specialist Router |
| Specialist Router | `specialist_route == "card"` | Card Specialist |
| Specialist Router | `specialist_route == "loan"` | Loan Specialist |
| Specialist Router | `specialist_route == "insurance"` | Insurance Specialist |
| Specialist Router | `specialist_route == "fraud"` | Fraud Specialist |
| Specialist Router | `specialist_route == "premium"` | Premium Specialist |
| Any Specialist | (always) | output_guardrails → Save Session → End |

---

## Early Exit Paths

The workflow can terminate early in these cases:

1. **Input blocked:** input_guardrails flags dangerous user message → fallback response, skip processing.
2. **Needs more info:** Greeter cannot verify identity; user must provide additional data (e.g., phone or IBAN).
3. **Identification failed:** User provided data but it does not match any customer (2/3 rule not satisfied).

In all cases, **output_guardrails** processes the response before it reaches the user. **input_guardrails** runs right after the user message to block dangerous requests before any processing.

---

## Session Persistence

Every path that reaches **END** goes through `save_session`, ensuring:

- Conversation history is preserved
- Collected identification data is retained for multi-turn flows
- The next message can resume from the correct state

---

*Next: [03 - Agent Responsibilities](./03-AGENTS.md)*
