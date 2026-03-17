# 🛡️ Bouncer Agent — Complete Explanation

Documentation of the Bouncer agent, its role in the flow, and how customer classification works.

---

## Role of the Bouncer

The Bouncer is the **second agent** in the flow. It runs **only when the customer has been identified** by the Greeter. It:

1. **Reads** — `customer_record` from the Greeter (contains `premium` flag)
2. **Classifies** — regular vs premium customer
3. **Sets** — `customer_type` and `priority_level` for downstream routing

---

## When Does the Bouncer Run?

The workflow uses conditional routing after the Greeter:

| Greeter outcome              | Next node   | Bouncer runs? |
|-----------------------------|-------------|---------------|
| `needs_more_info`           | Guardrails  | No            |
| `identification_failed`    | Guardrails  | No            |
| `is_identified`             | **Bouncer** | **Yes**       |

So the Bouncer only runs when the customer has been successfully verified against the database.

---

## Flow (1 step)

```
1. Read customer_record.premium
2. Set customer_type = "premium" | "regular"
3. Set priority_level = "high" | "normal"
```

---

## Classification Logic

| `customer_record.premium` | `customer_type` | `priority_level` |
|---------------------------|-----------------|-----------------|
| `True`                    | `premium`       | `high`          |
| `False` or missing        | `regular`       | `normal`        |

---

## Case 1: Premium Customer

**When:** `customer_record.premium` is `True`.

**Example:** Fabio Mesquita, Lisa (from `customers.json`).

**Output:**
```json
{
  "customer_type": "premium",
  "priority_level": "high"
}
```

---

## Case 2: Regular Customer

**When:** `customer_record.premium` is `False` or not present.

**Example:** John Smith (from `customers.json`).

**Output:**
```json
{
  "customer_type": "regular",
  "priority_level": "normal"
}
```

---

## Edge Cases

### Empty `customer_record`

If `customer_record` is `None` or `{}`, the Bouncer treats it as regular:

```json
{
  "customer_type": "regular",
  "priority_level": "normal"
}
```

### `not_customer`

The Bouncer does **not** set `customer_type: "not_customer"`. That path is handled by the Guardrails when `identification_failed` is true — the flow never reaches the Bouncer in that case.

---

## API Response

When the flow goes through the Bouncer, the `/chat` response includes:

```json
{
  "session_id": "...",
  "response": "Thanks, Fabio Mesquita. I've verified your identity.",
  "status": "completed",
  "customer_type": "premium",
  "route": null,
  "needs_more_info": false
}
```

- `customer_type` — `"premium"` or `"regular"` (set by Bouncer)
- `status` — `"completed"` when identified and classified

---

## Flow Diagram

```
                    Greeter output
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              route_after_greeter(state)                  │
│   needs_more_info or identification_failed?              │
└────────────────────────┬────────────────────────────────┘
                          │
           ┌──────────────┴──────────────┐
           │ Yes                         │ No (is_identified)
           ▼                             ▼
    ┌──────────────┐              ┌──────────────┐
    │  Guardrails  │              │   Bouncer    │
    │  (output checks)           │  customer_record.premium
    └──────┬───────┘              └──────┬───────┘
           │                             │
           │                    premium? │
           │                    ┌───────┴───────┐
           │                    │ Yes    │ No   │
           │                    ▼        ▼     │
           │              premium  regular     │
           │              high     normal     │
           │                    │        │    │
           └────────────────────┴────────┴────┘
                          │
                          ▼
                   save_session → END
```

---

## How to Test

### Unit tests

```bash
pytest tests/test_bouncer.py tests/test_routing.py -v
```

### API (full flow)

```bash
# Premium customer
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-1", "message": "Hi, I am Fabio Mesquita, phone 912345678"}'
# Expect: customer_type: "premium", status: "completed"

# Regular customer
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-2", "message": "Hi, I am John Smith, phone +44123456789"}'
# Expect: customer_type: "regular", status: "completed"
```

---

## Summary

The Bouncer is a simple, rule-based agent. It runs only when the Greeter has identified the customer. It reads `customer_record.premium` and sets `customer_type` (premium/regular) and `priority_level` (high/normal). These fields are used by the Specialist Router and Specialists for prioritisation and routing.

---

*Back to [Documentation Index](./README.md)*
