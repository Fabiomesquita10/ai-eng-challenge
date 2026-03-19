# 🏗️ Architecture Diagram

Visual representation of the Multi-Agent Banking Support system flow.

---

## System Flow

```mermaid
flowchart TD
    subgraph Entry[" "]
        User[👤 User Request]
        API[FastAPI /chat]
        SessionLoad[Session Manager<br/>Load Session]
    end

    subgraph GuardrailsIn["Input Guardrails"]
        InputCheck[Validate & Block<br/>Dangerous Requests]
    end

    subgraph Agents["Agents"]
        Greeter[Greeter Agent<br/>Identification & Intent<br/>2/3 verification]
        Bouncer[Bouncer Agent<br/>Customer Classification<br/>regular / premium / not customer]
        Router[Specialist Router<br/>rules + prompt + LLM fallback]
    end

    subgraph Specialists["Specialists"]
        Card[Card]
        Loan[Loan]
        Insurance[Insurance + RAG]
        Fraud[Fraud]
        Premium[Premium]
        General[General]
    end

    subgraph GuardrailsOut["Output Guardrails"]
        OutputCheck[Redact · Validate ·<br/>Safe Rewrite]
    end

    subgraph Exit[" "]
        SessionSave[Session Manager<br/>Save Session]
        Response[📤 Response]
    end

    User --> API
    API --> SessionLoad
    SessionLoad --> InputCheck

    InputCheck -->|blocked| OutputCheck
    InputCheck -->|OK| Greeter

    Greeter -->|needs_more_info| OutputCheck
    Greeter -->|identification_failed| OutputCheck
    Greeter -->|is_identified| Bouncer

    Bouncer --> Router

    Router --> Card
    Router --> Loan
    Router --> Insurance
    Router --> Fraud
    Router --> Premium
    Router --> General

    Card --> OutputCheck
    Loan --> OutputCheck
    Insurance --> OutputCheck
    Fraud --> OutputCheck
    Premium --> OutputCheck
    General --> OutputCheck

    OutputCheck --> SessionSave
    SessionSave --> Response
```

---

## Simplified High-Level View

```mermaid
flowchart LR
    A[User] --> B[FastAPI]
    B --> C[Input Guardrails]
    C --> D[Greeter]
    D --> E[Bouncer]
    E --> F[Specialist Router]
    F --> G[Specialists]
    G --> H[Output Guardrails]
    H --> I[Response]
```

---

## Routing Logic (Specialist Router)

```mermaid
flowchart TD
    Router[Specialist Router]
    Router -->|card intent| Card[Card Specialist]
    Router -->|loan intent| Loan[Loan Specialist]
    Router -->|insurance intent| Insurance[Insurance Specialist<br/>+ RAG over knowledge base]
    Router -->|fraud intent| Fraud[Fraud Specialist]
    Router -->|premium + high_value| Premium[Premium Specialist]
    Router -->|fallback| General[General Specialist]
```

---

## Early Exit Paths

```mermaid
flowchart TD
    subgraph EarlyExits["Early Exit Conditions"]
        A[Input Guardrails] -->|blocked| E1[End]
        B[Greeter] -->|needs_more_info| E2[End]
        B -->|identification_failed| E3[End]
    end

    E1 --> O[Output Guardrails]
    E2 --> O
    E3 --> O
```

---

*See [01-ARCHITECTURE.md](./01-ARCHITECTURE.md) for detailed component responsibilities.*
