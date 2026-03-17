# 🏦 Multi-Agent Banking Support System

An AI-powered customer support system that uses multiple specialized agents to identify customers and intelligently route their requests—eliminating the friction of traditional banking support flows.

---

## 🚀 Overview

This project implements a **multi-agent architecture** where different AI agents collaborate to:

* Identify and verify customers using partial information
* Classify customers (regular, premium, or unknown)
* Route requests to the appropriate specialist
* Ensure safety, compliance, and professional responses

The system is designed to mimic a real-world banking support workflow while showcasing strong **AI engineering practices**, including orchestration, modular design, and controlled use of LLMs.

---

## 📚 Architecture Documentation

For detailed architecture documentation (workflow, agent responsibilities, design principles), see the **[docs/](./docs/)** folder:

- [System Architecture](./docs/01-ARCHITECTURE.md)
- [Orchestration Workflow](./docs/02-WORKFLOW.md)
- [Agent Responsibilities](./docs/03-AGENTS.md)
- [Design Principles](./docs/04-DESIGN_PRINCIPLES.md)
- [Why LangGraph](./docs/05-WHY_LANGGRAPH.md)
- [Model Configuration & RAG](./docs/06-MODEL_TRAINING_AND_RAG.md)

---

## 🧠 System Architecture

The system is built around a **LangGraph-based orchestration layer**, where each node represents a specialized agent.

### High-Level Flow

```
User → FastAPI → Greeter → Bouncer → Specialist Router → Specialist → Guardrails → Response
```

A **lightweight RAG component** is used inside the **Insurance Specialist Agent** to ground responses on a small internal knowledge base of insurance products, specialty coverage areas, and routing policies. This demonstrates retrieval-augmented reasoning where it adds real value, rather than using retrieval for simple routing decisions.

### Agents

#### 👋 Greeter Agent

* Starts the conversation
* Extracts intent and identification data (name, phone, IBAN)
* Verifies customer legitimacy (2 out of 3 rule)
* Requests missing information when needed

#### 🛡️ Bouncer Agent

* Classifies the customer:

  * Regular
  * Premium
  * Not a customer
* Applies eligibility rules

#### 📞 Specialist Router Agent

* Rule-first + prompt engineering + LLM fallback (no RAG — rules suffice for routing)
* Determines the correct domain expert based on:

  * User intent
  * Customer type
  * High-value flag

#### 🎯 Specialist Agents

Dedicated agents for handling specific domains:

* Card Support
* Loans
* **Insurance** *(uses RAG over insurance knowledge base for grounded responses)*
* Fraud
* Premium Services

#### 📜 Guardrails

* Ensures compliance with banking policies
* Prevents unsafe or out-of-scope responses
* Validates both user input and system output

---

## 🔁 Orchestration (LangGraph)

Agents do not directly call each other.

Instead:

* Each agent updates a shared **conversation state**
* The orchestration layer routes execution based on that state

This ensures:

* Clear separation of concerns
* Deterministic control flow
* Testability and scalability

---

## 🧩 State Management

All agents share a structured state object:

```python
ConversationState = {
    "session_id": str,
    "user_message": str,
    "conversation_history": list,

    "collected_data": {
        "name": str | None,
        "phone": str | None,
        "iban": str | None
    },

    "intent": str | None,
    "is_identified": bool,
    "needs_more_info": bool,

    "customer_type": str | None,
    "specialist_route": str | None,

    "final_response": str | None
}
```

This enables:

* Multi-turn conversations
* Memory of previously provided data
* Incremental reasoning

---

## ⚙️ Tools & Design Philosophy

Each agent uses a set of **tools** (functions/services) to perform specific tasks.

### Key Principles

* **LLMs are used selectively**, for:

  * Intent extraction
  * Entity extraction
  * Natural language responses

* **Deterministic logic is used for:**

  * Identity verification (2/3 rule)
  * Customer classification
  * Routing logic
  * Policy enforcement

This hybrid approach ensures both:

* Flexibility (AI)
* Reliability (engineering)

---

## 🔐 Identity Verification

Customer legitimacy is determined using a **2 out of 3 rule**:

* Name
* Phone number
* IBAN

At least two must match a known customer record.

This is implemented using deterministic logic to guarantee consistency and correctness.

---

## 🧭 Routing Logic

Requests are routed based on:

* Intent (e.g., card issue, loan request, insurance)
* Customer type (regular vs premium)
* Special cases (e.g., fraud, high-value services)

Example:

* “Lost my card” → Card Specialist
* “Yacht insurance” → Insurance Specialist
* Premium + wealth request → Premium Specialist

---

## 🛡️ Guardrails

The system enforces strict policies:

* Blocks unsafe requests (e.g., unauthorized actions)
* Prevents data leakage
* Ensures responses remain within system scope
* Rewrites unsafe outputs if necessary

---

## 🧪 Testing

```bash
pytest tests/ -v
```

**Test coverage:**
* `test_verification.py` — 2/3 rule, phone/name normalization
* `test_response_builder.py` — merge, missing fields, response building
* `test_greeter.py` — greeter flows (mocked extraction)
* `test_api.py` — `/health`, `/chat` endpoints

---

## 🌐 API

### POST `/chat`

```json
{
  "session_id": "abc-123",
  "message": "Hi, I lost my card"
}
```

### Response

```json
{
  "response": "Thanks, Fabio. To verify your identity, could you provide your phone number or IBAN?"
}
```

---

## 🐳 Running the Project

**Prerequisite:** Create a `.env` file with your OpenAI API key:

```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-your-actual-key
```

**Production:**
```bash
docker compose up --build
```

**Development (with reload):**
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```
Code changes in `app/` and `docs/` will trigger an automatic reload.

**Local (no Docker):**
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Insurance RAG (InsuranceQA-v2 + FAISS)

The Insurance Specialist uses [InsuranceQA-v2](https://huggingface.co/datasets/deccan-ai/insuranceQA-v2) with **FAISS** for vector search. When running with Docker, the dataset (1000 docs) is loaded and the FAISS index is pre-built on container startup. For local development:

```bash
python scripts/load_insurance_qa.py --max-rows 2000
```

Options: `--max-rows 0` for all ~28k pairs; `--split validation` or `--split test`. The FAISS index is built on first Insurance query and cached in `app/data/faiss_insurance/`.

---

## 📌 Design Decisions

* Used **LangGraph** for explicit orchestration and state-driven routing
* Separated agents by responsibility to reflect real-world systems
* Avoided overusing LLMs in deterministic logic
* Implemented session-based memory for multi-turn interactions
* **RAG in Insurance Specialist** — grounds responses in an internal knowledge base of insurance products and specialty coverage, where retrieval adds real value (rather than using RAG for simple routing)

---

## 🤝 Final Notes

This project aims to demonstrate not just AI capabilities, but **strong system design, clarity of architecture, and production-oriented thinking**.

---

Made with a focus on clean architecture, reliability, and real-world applicability.