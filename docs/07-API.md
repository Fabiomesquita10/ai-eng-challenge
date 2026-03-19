# 🌐 API Contract

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/chat` | Process user message, return system response |
| GET | `/health` | Health check |

---

## POST /chat

### Request

```json
{
  "session_id": "abc-123",
  "message": "Hi, I need help with my yacht insurance"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| session_id | string | Yes | Unique session identifier (enables multi-turn) |
| message | string | Yes | User message (min 1 character) |

### Response

```json
{
  "session_id": "abc-123",
  "response": "Thanks, Fabio. I've verified your identity and routed your request to our specialist insurance team.",
  "status": "completed",
  "customer_type": "premium",
  "route": "insurance",
  "needs_more_info": false
}
```

| Field | Type | Description |
|-------|------|-------------|
| session_id | string | Same as request |
| response | string | Text returned to the user |
| status | string | `needs_more_info` \| `completed` \| `rejected` \| `error` |
| customer_type | string \| null | `regular` \| `premium` \| `not_customer` |
| route | string \| null | `card` \| `loan` \| `insurance` \| `fraud` \| `premium` |
| needs_more_info | boolean | True if more identification data is needed |

### Status Values

| Status | Meaning |
|--------|--------|
| `needs_more_info` | Missing identification data; user must provide more info |
| `completed` | Request handled / routed successfully |
| `rejected` | Blocked by guardrails or customer not eligible |
| `error` | Technical error |

### State → Status Mapping

```
guardrail_flagged     → rejected
needs_more_info       → needs_more_info
customer_type == "not_customer" → rejected
identification_failed → rejected
final_response        → completed
otherwise             → error
```

---

## GET /health

### Response

```json
{
  "status": "ok"
}
```

---

## Example Responses

### 1. Needs more info

```json
{
  "session_id": "abc-123",
  "response": "Thanks, Fabio. To verify your identity, could you please provide your phone number or IBAN?",
  "status": "needs_more_info",
  "customer_type": null,
  "route": null,
  "needs_more_info": true
}
```

### 2. Completed

```json
{
  "session_id": "abc-123",
  "response": "Thanks, Fabio. I've verified your identity and routed your request to our priority card support team.",
  "status": "completed",
  "customer_type": "premium",
  "route": "card",
  "needs_more_info": false
}
```

### 3. Rejected (not a customer)

```json
{
  "session_id": "abc-123",
  "response": "I'm sorry, I couldn't verify your details in our system. If you're a new customer, I can guide you to our onboarding team.",
  "status": "rejected",
  "customer_type": "not_customer",
  "route": null,
  "needs_more_info": false
}
```

### 4. Rejected (guardrail)

```json
{
  "session_id": "abc-123",
  "response": "I can help guide you through our banking services, but I can't perform that action directly.",
  "status": "rejected",
  "customer_type": null,
  "route": null,
  "needs_more_info": false
}
```

---

*Back to [Documentation Index](./README.md)*
