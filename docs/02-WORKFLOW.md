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
greeter_agent
  │
  ├── needs_more_info ──────► guardrails ──► save_session ──► END
  │
  ├── identification_failed ─► guardrails ──► save_session ──► END
  │
  └── is_identified ────────► bouncer_agent
                                │
                                ├── not_customer ──► guardrails ──► save_session ──► END
                                │
                                └── regular/premium ─► specialist_router_agent
                                                        │   (rules + prompt + LLM fallback)
                                                        │
                                                        ├── card ──────► card_specialist
                                                        ├── loan ──────► loan_specialist
                                                        ├── insurance ─► insurance_specialist (RAG)
                                                        ├── fraud ─────► fraud_specialist
                                                        └── premium ───► premium_specialist
                                                                          │
                                                                          ▼
                                                                     guardrails
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
| Greeter | `needs_more_info == True` | Guardrails → End |
| Greeter | `identification_failed == True` | Guardrails → End |
| Greeter | `is_identified == True` | Bouncer |
| Bouncer | `customer_type == "not_customer"` | Guardrails → End |
| Bouncer | `customer_type in ["regular", "premium"]` | Specialist Router |
| Specialist Router | `specialist_route == "card"` | Card Specialist |
| Specialist Router | `specialist_route == "loan"` | Loan Specialist |
| Specialist Router | `specialist_route == "insurance"` | Insurance Specialist |
| Specialist Router | `specialist_route == "fraud"` | Fraud Specialist |
| Specialist Router | `specialist_route == "premium"` | Premium Specialist |
| Any Specialist | (always) | Guardrails → Save Session → End |

---

## Early Exit Paths

The workflow can terminate early in these cases:

1. **Needs more info:** Greeter cannot verify identity; user must provide additional data (e.g., phone or IBAN).
2. **Identification failed:** User provided data but it does not match any customer (2/3 rule not satisfied).
3. **Not a customer:** Bouncer determines the user is not a customer; request cannot proceed.

In all early-exit cases, the **Guardrails** layer still processes the response to ensure it is safe and compliant before returning to the user.

---

## Session Persistence

Every path that reaches **END** goes through `save_session`, ensuring:

- Conversation history is preserved
- Collected identification data is retained for multi-turn flows
- The next message can resume from the correct state

---

*Next: [03 - Agent Responsibilities](./03-AGENTS.md)*
