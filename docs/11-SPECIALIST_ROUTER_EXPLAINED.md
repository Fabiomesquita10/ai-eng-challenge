# 📞 Specialist Router — Complete Explanation

Documentation of the Specialist Router: rule-based intent → specialist_route mapping.

---

## Role of the Specialist Router

The Specialist Router runs **after the Bouncer** when the customer has been identified. It:

1. **Reads** — `intent` from the Greeter
2. **Maps** — intent to specialist route (card, loan, insurance, fraud, premium, general)
3. **Sets** — `specialist_route` and `route_reason` for downstream specialists

---

## When Does It Run?

| Path | Specialist Router runs? |
|------|-------------------------|
| `needs_more_info` → Guardrails | No |
| `identification_failed` → Guardrails | No |
| `is_identified` → Bouncer → **Specialist Router** | **Yes** |

---

## Approach: Rule-Based Only

No LLM. A simple dictionary maps `intent` → `specialist_route`:

| Intent (from Greeter) | specialist_route |
|----------------------|------------------|
| card | card |
| loan | loan |
| insurance | insurance |
| fraud | fraud |
| premium | premium |
| general_support | general |
| *unknown / empty* | **general** (fallback) |

---

## Fallback: General

When the intent is unknown, empty, or not in the mapping, the Router uses **general** as the fallback route. A General Specialist handles:

- Ambiguous requests
- General inquiries ("I need help", "I have a question")
- Intents that don't fit card/loan/insurance/fraud/premium

---

## Flow

```
Bouncer (customer_type, priority_level)
    │
    ▼
Specialist Router
    │  intent → specialist_route
    ▼
Guardrails → save_session → END
```

---

## Output

```json
{
  "specialist_route": "card",
  "route_reason": "intent=card"
}
```

- `specialist_route` — which specialist will handle the request (when specialists are implemented)
- `route_reason` — debug info (e.g. `intent=card` or `intent unknown`)

---

## API Response

When the flow goes through the Specialist Router, the `/chat` response includes:

```json
{
  "session_id": "...",
  "response": "Thanks, Fabio Mesquita. I've verified your identity.",
  "status": "completed",
  "customer_type": "premium",
  "route": "card",
  "needs_more_info": false
}
```

- `route` — the `specialist_route` (card, loan, insurance, fraud, premium, general)

---

## How to Test

```bash
pytest tests/test_specialist_router.py tests/test_api.py -v -k "identified or route"
```

---

## Next Step: Specialists

The Specialist Router sets `specialist_route`. The next implementation step is the **Specialists** — agents that consume this route and generate the final response. Until then, the Greeter's `final_response` (e.g. "Thanks, X. I've verified your identity.") is returned as-is.

---

*Back to [Documentation Index](./README.md)*
