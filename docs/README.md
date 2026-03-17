# Multi-Agent Banking Support — Architecture Documentation

This folder contains the technical architecture documentation for the AI-powered customer support system, designed for the **AI Engineer Code Challenge**.

---

## 📚 Documentation Index

| Document | Description |
|----------|-------------|
| [01 - System Architecture](./01-ARCHITECTURE.md) | High-level system overview and component flow |
| [02 - Orchestration Workflow](./02-WORKFLOW.md) | LangGraph flow, routing logic, and state transitions |
| [03 - Agent Responsibilities](./03-AGENTS.md) | Detailed responsibilities of each agent |
| [04 - Design Principles](./04-DESIGN_PRINCIPLES.md) | Core design decisions and engineering philosophy |
| [05 - Why LangGraph](./05-WHY_LANGGRAPH.md) | Rationale for using LangGraph as the orchestration framework |
| [06 - Model Configuration & RAG](./06-MODEL_TRAINING_AND_RAG.md) | Model setup per agent, prompt design, and RAG strategy (Specialist Router) |

---

## 🎯 Challenge Context

The system addresses the following business problem:

> A customer calls the bank, hoping to get help, but instead, they get lost in an endless phone menu maze.

**Mission:** Build an AI-powered customer support system where multiple agents collaborate to:

- **Identify** the customer  
- **Classify** them (regular, premium, or not a customer)  
- **Route** their request to the correct specialist  

All of this should happen **seamlessly**, without the friction of traditional IVR systems.

---

## 🏗️ Quick Reference

```
User Request → FastAPI (/chat) → Session Manager → Greeter → Bouncer → Specialist Router → Specialist → Guardrails → Response
```

---

*For implementation details, see the main [README](../README.md) in the project root.*
