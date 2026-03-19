# 👋 Greeter Agent — Complete Explanation

Documentation of the Greeter agent flow, decision logic, and all possible outcomes.

---

## Role of the Greeter

The Greeter is the **first agent** in the flow. It:

1. **Extracts** — intent and identification data (name, phone, IBAN)
2. **Accumulates** — merges new data with what already exists in the session
3. **Verifies** — applies the 2/3 rule against the customer database
4. **Secret question** — if customer has one, asks it before final identification

---

## Flow (7 steps)

```
1. extract_intent(message)           → intent + confidence
2. extract_identification(message)   → name, phone, iban (from current message)
3. merge_collected_data(existing, new) → accumulated data
4. compute_missing_fields()          → what's missing
5. has_minimum_identification_data? → 2+ fields filled?
6. If yes → verify_legitimacy()      → 2/3 rule
7. If 2/3 match + customer has secret → ask secret question (needs_more_info)
   If 2/3 match + no secret          → is_identified
   If waiting for secret answer      → verify answer → is_identified or identification_failed
```

---

## Decision: 4 possible outcomes

| Condition | Result | Typical message |
|-----------|--------|-----------------|
| **< 2 fields** | `needs_more_info = True` | "Could you please provide your phone number or IBAN?" |
| **2+ fields + match + has secret** | `needs_more_info = True` | "For security, please answer: Which is the name of my dog?" |
| **2+ fields + match + no secret** | `is_identified = True` | "Thanks, [name]. I've verified your identity." |
| **2+ fields + match + secret answer correct** | `is_identified = True` | "Thanks, [name]. I've verified your identity." |
| **2+ fields + match + secret answer wrong** | `identification_failed = True` | "I couldn't verify your details..." |
| **2+ fields + no match** | `identification_failed = True` | "I couldn't verify your details with the information provided." |

---

## Case 1: `needs_more_info`

**When:** User has provided fewer than 2 identification fields (name, phone, iban).

**Examples:**
- Message 1: "Hi, I need help" → no identification data
- Message 2: "My name is Fabio" → only name
- Message 3: "My phone is 912345678" (no name) → only phone

**What happens:**
- Greeter does not call `verify_legitimacy`
- Computes `missing_fields` (e.g. `["phone", "iban"]`)
- Builds personalized response if name is already known

**Output:**
```json
{
  "needs_more_info": true,
  "is_identified": false,
  "identification_failed": false,
  "missing_fields": ["phone", "iban"],
  "final_response": "Thanks, Fabio. To verify your identity, could you please provide your phone number or IBAN?"
}
```

---

## Case 2a: `needs_more_info` (secret question)

**When:** 2+ fields match a customer who has a `secret` and `answer` in the database.

**What happens:**
- Greeter calls `verify_legitimacy(collected_data)` → match
- Customer record has `secret` (question) and `answer`
- Greeter asks the secret question instead of identifying immediately
- Stores `customer_record` and `secret_question` in session for next turn

**Output:**
```json
{
  "needs_more_info": true,
  "is_identified": false,
  "identification_failed": false,
  "customer_record": { "name": "Lisa", "secret": "Which is the name of my dog?", "answer": "Yoda", ... },
  "secret_question": "Which is the name of my dog?",
  "final_response": "For security, please answer: Which is the name of my dog?"
}
```

**Next turn:** User provides answer (e.g. "Yoda"). Greeter verifies against `customer_record.answer`. If match → `is_identified`; if not → `identification_failed`.

---

## Case 2b: `is_identified`

**When:** 2+ fields match a customer with no secret, or secret answer was correct.

**2/3 rule:** At least 2 of (name, phone, iban) must match a customer record.

**Examples:**
- Name + phone → match, no secret → identified
- Name + IBAN → match, secret answered correctly → identified
- Phone + IBAN → match, no secret → identified

**What happens:**
- Greeter calls `verify_legitimacy(collected_data)`
- If customer has no `secret`/`answer` → identify immediately
- If customer has secret and we're on the answer turn → verify answer (normalized, substring match)

**Output:**
```json
{
  "is_identified": true,
  "needs_more_info": false,
  "identification_failed": false,
  "customer_record": {
    "name": "Fabio Mesquita",
    "phone": "912345678",
    "iban": "PT50...",
    "premium": true
  },
  "final_response": "Thanks, Fabio Mesquita. I've verified your identity."
}
```

---

## Case 3: `identification_failed`

**When:** 2+ fields are filled but no customer in the database matches.

**Examples:**
- Name + phone of someone not in `customers.json`
- Wrong data or non-existent customer

**What happens:**
- Greeter calls `verify_legitimacy(collected_data)`
- No customer satisfies the 2/3 rule
- Returns `identification_failed = True`

**Output:**
```json
{
  "identification_failed": true,
  "is_identified": false,
  "needs_more_info": false,
  "final_response": "I'm sorry, I couldn't verify your details with the information provided. If you're a new customer, I can guide you to our onboarding team."
}
```

---

## Special cases

### Multi-turn

- Greeter uses `collected_data` from the session
- Merge: new data overwrites or fills existing fields
- Example: "My name is Fabio" → only name; later "My phone is 912345678" → name + phone → verification

### Merge

- `merge_collected_data(existing, new)`
- New non-empty values override existing ones
- Example: "fabio" → "Fabio Mesquita" when user corrects

### Verification normalization

- **Phone:** digits only
- **IBAN:** uppercase, no spaces
- **Name:** lowercase for comparison

---

## Summary

The Greeter extracts intent and identification data (name, phone, IBAN) using an LLM, merges it with the session, and applies the 2/3 rule. If there are fewer than 2 fields, it asks for more. If there are 2 or more and match, it checks for a secret question: if present, it asks it and waits for the answer; if absent, it identifies immediately. If the secret answer is wrong, identification fails. The merge supports multi-turn: the user can provide data across multiple messages.

---

## Flow diagram

```
                    User message
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Extraction (LLM)                      │
│              intent + name, phone, iban                  │
└────────────────────────┬────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Merge with session                    │
│              collected_data (accumulated)                │
└────────────────────────┬────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  ≥ 2 fields filled?                       │
└────────────────────────┬────────────────────────────────┘
                          │
           ┌──────────────┼──────────────┐
           │ No           │ Yes         │
           ▼              ▼             │
  needs_more_info   verify_legitimacy  │
           │              │             │
           │     ┌────────┴────────┐    │
           │     │ Match in DB?   │    │
           │     └────────┬───────┘    │
           │     Yes      │ No         │
           │     ▼        ▼            │
           │  is_identified  identification_failed
           │     │        │            │
           └────┴────────┴────────────┘
```

---

*Back to [Documentation Index](./README.md)*
