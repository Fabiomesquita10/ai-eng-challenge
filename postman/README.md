# Postman Collection — Multi-Agent Banking Support

## Import

1. Open Postman
2. File → Import → Select `Multi-Agent-Banking-Support.postman_collection.json`
3. The collection includes a `base_url` variable (default: `http://localhost:8000`)

## Prerequisites

- App running: `docker compose up` or `uvicorn app.main:app --reload`
- `.env` with `OPENAI_API_KEY` set

## Folders & Cases

| Folder | Request | Description |
|--------|---------|-------------|
| **1. Health** | GET Health | `status: ok` |
| **2. Input Guardrail** | Input Blocked | Dangerous message → `rejected`, fallback |
| **3. Greeter - Needs More Info** | First message, Only name, Only phone | Asks for identification |
| **4. Greeter - Identification Failed** | Unknown customer | `rejected` |
| **5. Specialists** | Card, Loan, Insurance, Fraud, Premium, General | One per specialist route |
| **6. Customer Types** | Premium (Fabio), Regular (John) | `customer_type` |
| **7. Output Guardrail** | Trigger | `test_output_guardrail_inject` → flagged |
| **8. Multi-turn** | Turn 1 + Turn 2 | Same `session_id`, identification flow |

## Test Customers (from conftest)

- **Fabio Mesquita** — phone 912345678, IBAN PT50... — premium
- **John Smith** — phone +44123456789, IBAN GB82... — regular
- **Lisa** — phone +1122334455, IBAN DE89... — premium

## Change base_url

Edit collection variables or create a Postman Environment with `base_url` (e.g. `http://localhost:8000`).
