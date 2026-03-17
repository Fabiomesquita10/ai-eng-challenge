# 🧩 Agent Responsibilities

Each agent has a **single, well-defined role** within the system. This document describes what each agent does and what it is responsible for.

---

## 👋 Greeter Agent

**Role:** Entry point of the system.

**Responsibilities:**

| Task | Description |
|------|-------------|
| Extract intent | Parse the user message to understand what they want (e.g., card issue, loan, insurance) |
| Extract identification data | Pull name, phone, and IBAN from user input |
| Merge with session memory | Combine new data with previously collected data from the conversation |
| Verify customer legitimacy | Apply the **2 out of 3 rule** (name, phone, IBAN) against known customers |
| Request missing information | If verification fails due to insufficient data, ask for what is missing |

**Outputs (state updates):**

- `collected_data` (name, phone, iban)
- `intent`
- `is_identified` (boolean)
- `needs_more_info` (boolean)
- `identification_failed` (boolean)

---

## 🛡️ Bouncer Agent

**Role:** Customer classification.

**Responsibilities:**

| Task | Description |
|------|-------------|
| Determine customer type | Classify the user as one of: **Regular customer**, **Premium customer**, or **Not a customer** |
| Apply eligibility rules | Decide whether the request can proceed based on customer status |
| Gate access | Block non-customers from specialist routing |

**Outputs (state updates):**

- `customer_type` ("regular" | "premium" | "not_customer")

**Note:** This logic is typically **deterministic** (rule-based), not LLM-driven, to ensure consistent classification.

---

## 📞 Specialist Router Agent

**Role:** Routing decision engine.

**Responsibilities:**

| Task | Description |
|------|-------------|
| Map intent to domain | Translate user intent into a specialist route (card, loan, insurance, fraud, premium) |
| Detect high-value requests | Identify special cases (e.g., yacht insurance, wealth management) via `high_value` flag |
| Route to correct specialist | Select the appropriate specialist agent based on intent and customer type |

**Outputs (state updates):**

- `specialist_route` ("card" | "loan" | "insurance" | "fraud" | "premium")
- `high_value` (boolean, optional)

**Approach:** Rule-first + prompt engineering + few-shot examples. LLM fallback for ambiguous intents. **No RAG** — with a handful of well-defined routes, rules and prompts suffice.

**Example mappings:**

- "Lost my card" → Card Specialist
- "Yacht insurance" → Insurance Specialist
- Premium customer + wealth request → Premium Specialist
- "Suspicious transaction" → Fraud Specialist

---

## 🎯 Specialist Agents

**Role:** Domain-specific handlers.

Each specialist handles requests within its domain and generates appropriate responses.

| Specialist | Domain | Example intents | RAG? |
|------------|--------|-----------------|------|
| **Card Specialist** | Card issues, blocking, replacement | Lost card, stolen card, PIN reset | No |
| **Loan Specialist** | Loans, mortgages, credit | Loan application, interest rates | No |
| **Insurance Specialist** | Insurance products | Car insurance, yacht insurance, claims | **Yes** |
| **Fraud Specialist** | Fraud detection, disputes | Suspicious transactions, dispute a charge | No |
| **Premium Specialist** | High-value, VIP services | Wealth management, concierge, premium products | No |

**Insurance Specialist RAG:** Retrieves from an internal knowledge base (insurance products, specialty coverage, routing policies) to ground responses. Example: "I need help with my yacht insurance policy" → retrieval finds marine/specialty insurance docs → response is grounded in actual documentation.

**Outputs (state updates):**

- `final_response` (the generated reply to the user)

---

## 📜 Guardrails

**Role:** Safety and compliance layer.

**Responsibilities:**

| Task | Description |
|------|-------------|
| Validate user input | Ensure the user message does not contain unsafe or out-of-scope content |
| Validate system output | Check that the generated response complies with policies |
| Prevent unsafe actions | Block requests that could lead to unauthorized approvals or data leaks |
| Enforce policy constraints | Ensure responses stay within banking scope and professional tone |
| Rewrite if necessary | If output is unsafe, sanitize or replace it before returning |

**When it runs:**

- After Greeter (when `needs_more_info` or `identification_failed`)
- After Bouncer (when `not_customer`)
- After every Specialist (before `save_session` and END)

---

## Summary Table

| Agent | Primary responsibility | LLM used? |
|-------|------------------------|-----------|
| Greeter | Identification & intent extraction | Yes (extraction) |
| Bouncer | Customer classification | Optional (can be rule-based) |
| Specialist Router | Routing decision | Rule-based + optional LLM fallback |
| Specialists | Domain handling & response generation | Yes |
| Guardrails | Safety & compliance | Optional (validation logic) |

---

*Next: [04 - Design Principles](./04-DESIGN_PRINCIPLES.md)*
