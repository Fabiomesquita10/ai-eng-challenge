# 🤖 AI Engineer Code Challenge

## 🎯 Business Requirements

A customer calls the bank, hoping to get help, but instead, they get lost in an endless phone menu maze.

Nightmare, right? Well — not on our watch.

### 🚀 Mission

Build an **AI-powered customer support system** where multiple agents collaborate to:

* Identify the customer
* Classify them
* Route their request to the correct specialist

All of this should happen **seamlessly**, without the friction of traditional IVR systems.

---

## 🤝 Multi-Agent System

The system should be composed of multiple AI agents working together:

### 👋 Agent 1: The Greeter

* Starts the conversation
* Requests identification details
* Extracts relevant information from user input
* Verifies that the customer is legitimate

---

### 🛡️ Agent 2: The Bouncer

* Activated after the customer is identified
* Classifies the user into:

  * Regular customer
  * Premium customer
  * Not a customer
* Determines whether the request can proceed

---

### 📞 Agent 3: The Specialist

* Handles routing to the correct expert
* Detects high-value or specific requests (e.g. yacht insurance 🛥️)
* Ensures the user reaches the appropriate domain specialist

---

### 📜 Guardrails: The Rule Enforcer

* Ensures compliance with banking policies
* Prevents unsafe or out-of-scope behavior
* Avoids actions such as unauthorized approvals or data leaks

---

## 🛠️ Technical Requirements

### 🏗️ Framework & Structure

* You are free to use **LangGraph** or a similar orchestration framework
* A **Jupyter Notebook is acceptable**, but structure and design will be evaluated

---

### 🧠 LLM Choice

* You may use any LLM of your choice
* ⚠️ Make sure to remove API keys before submission

---

### ⚙️ Core Logic

* The system must verify a customer using **at least 2 out of 3 fields**:

  * Name
  * Phone number
  * IBAN

* Only after verification should further processing continue

---

### 🚀 API Endpoint

* Expose your solution via a **FastAPI endpoint**
* Simulate a real-world interaction (e.g. `/chat` endpoint)

---

### 📄 Supporting Material

* Example data structures
* Expected responses

---

## 📦 Deliverables

### 📈 Architecture Diagram

* A visual representation of the system workflow
* Should clearly show agent interactions and routing logic

---

### 💻 Working Code

* Full implementation of the system
* Clean, modular, and maintainable structure
* Includes unit tests for key logic

---

### 📄 Pull Request(s)

* Use a **GitFlow-style approach**
* Submit features through one or more PRs

---

### 💬 Realistic Commits

* Maintain a clean and logical commit history
* Use descriptive commit messages

---

### 📤 Submission

* Commit and push your solution directly to the repository

---

## ✨ Bonus Points

Want to stand out? Consider implementing:

### 🗣️ Voice Interface

* Add **Speech-to-Text (STT)** and **Text-to-Speech (TTS)**

---

### 🔒 Advanced Guardrails

* More sophisticated safety and policy enforcement mechanisms

---

### 📚 Conversation Memory

* Store and use conversation history for better context awareness

---

### 🧪 Comprehensive Testing

* Expand unit and integration test coverage

---

### 🚀 CI/CD Pipeline

* Automate testing and deployment

---

### 🐳 Dockerization

* Package the application in a Docker container
* Enable easy deployment and scalability

---

## 🎉 Final Note

Now go ahead and build the most epic **AI-powered customer support system** ever.

Good luck — and have fun with it 🚀
