---
title: OpenEnv Support AI
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# 🧠 OpenEnv Support AI — Real-World Customer Support Simulation

## 🚀 Overview

This project implements a **real-world customer support environment** using the OpenEnv standard.
It simulates how AI agents handle customer tickets involving classification, response, escalation, and resolution.

The environment is designed to evaluate **multi-step reasoning**, **decision-making under constraints**, and **task completion efficiency**.

---

## 🎯 Motivation

Modern AI agents are increasingly used in:

* Customer support automation
* Helpdesk systems
* SaaS operations

This environment provides a **realistic benchmark** to test such agents in:

* Handling user intent
* Managing urgency (SLA)
* Making correct operational decisions

---

## 🧩 Environment Design

### 🔹 Observation Space

Each step provides structured information:

* `ticket_id`
* `customer_message`
* `customer_tier`
* `sentiment`
* `time_waiting`
* `previous_actions`
* `sla_remaining`
* `difficulty`

---

### 🔹 Action Space

Agents can perform:

* `classify` → Identify ticket category
* `reply` → Respond to customer
* `escalate` → Forward to higher support
* `close` → Resolve ticket

---

## 🧪 Tasks (Difficulty Levels)

| Level     | Description                                   |
| --------- | --------------------------------------------- |
| 🟢 Easy   | Simple classification tasks                   |
| 🟡 Medium | Requires escalation decisions                 |
| 🔴 Hard   | Full lifecycle handling under SLA constraints |

---

## 🧠 Real-World Features

* ⏱️ **SLA Deadlines** — penalties for delays
* 📊 **Difficulty Levels** — increasing complexity
* ⚠️ **Escalation Logic** — required for technical issues
* 🔁 **Multi-step Workflow** — not single-step decisions

---

## 🏆 Reward Design

The reward system is **dense and realistic**:

### ✅ Positive Rewards

* Correct classification
* Appropriate escalation
* Proper response
* Successful closure

### ❌ Penalties

* Wrong classification
* Ignoring escalation
* Delays (SLA violations)
* Inefficient action sequences

---

## 📏 Evaluation (Grader)

Each episode is scored between **0.0 → 1.0** based on:

* Action correctness
* Decision quality
* Workflow completion
* Efficiency

The grader is:

* Deterministic ✔
* Context-aware ✔
* Non-constant ✔

---

## 🤖 Baseline Agent

A rule-based agent is provided that:

* Performs keyword-based classification
* Decides escalation based on context
* Completes tasks in structured steps

### ▶ Run baseline:

```bash
python -m scripts.run_baseline
```

---

## 🐳 Docker Setup

### Build:

```bash
docker build -t support-env .
```

### Run:

```bash
docker run support-env
```

---

## ☁️ Deployment

This environment is deployed on Hugging Face Spaces.

👉 **Live Demo:**
https://huggingface.co/spaces/mano678/openenv-support-ai

---

## 📦 Project Structure

```
openenv-support-ai/
│
├── env/
│   ├── environment.py
│   ├── models.py
│   ├── reward.py
│   ├── graders.py
│   └── tasks.py
│
├── data/
├── scripts/
├── Dockerfile
├── requirements.txt
├── openenv.yaml
└── README.md
```

---

## ✅ OpenEnv Compliance

* ✔ step(action)
* ✔ reset()
* ✔ state()
* ✔ Typed models (Pydantic)
* ✔ openenv.yaml

---

## 🔁 Reproducibility

* Deterministic environment
* Consistent baseline scores
* Fully containerized via Docker

---

## 🧠 Key Strengths

* Real-world applicability
* Multi-step reasoning environment
* Strong reward shaping
* Robust grading system
* Fully deployable and reproducible

---

## 🚀 Future Improvements

* Multi-ticket queue system
* Customer satisfaction scoring
* Tool usage simulation (refund API)
* LLM-based response evaluation

---

## 📌 Conclusion

This project provides a **high-quality benchmark environment** for evaluating AI agents in realistic customer support workflows.

It balances:

* realism
* complexity
* reproducibility

making it suitable for both research and production-level evaluation.

---
