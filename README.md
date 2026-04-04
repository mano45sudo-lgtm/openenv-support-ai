---
title: OpenEnv Support AI
emoji: "🤖"
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# OpenEnv Support AI — Customer Support Simulation Environment

## Overview

This project implements a realistic customer support environment using the OpenEnv standard. It simulates how AI agents process support tickets through classification, response generation, escalation to specialist teams, and final resolution.

The environment is designed to evaluate multi-step reasoning, decision quality, and the ability to operate under real-world constraints such as SLA deadlines, customer satisfaction, and trust dynamics.

---

## Motivation

Customer support is one of the most widely deployed AI applications, yet most evaluation setups reduce it to simple classification tasks.

This environment models a more realistic system by introducing:

* Sequential decision-making
* Delayed effects of actions
* Customer interaction dynamics
* Internal escalation workflows
* Business-driven evaluation metrics

---

## Environment Design

### Observation Space

Each step returns structured data:

* `ticket_id`
* `customer_message`
* `customer_tier`
* `sentiment`
* `time_waiting`
* `previous_actions`

Additional signals:

* `conversation_history` — full interaction trace
* `sla_remaining` — remaining time before SLA violation
* `priority` — urgency level
* `difficulty` — task complexity
* `trust_score` — long-term customer confidence

---

### Action Space

Agents can perform:

* `classify` → Identify ticket category
* `reply` → Respond to customer
* `escalate` → Route to specialist team
* `close` → Close the ticket

---

## Real-World Mechanics

### Specialist Escalation

Escalation triggers a simulated specialist response instead of ending the episode. This models real internal workflows where issues are resolved by dedicated teams before closure.

---

### Customer Interaction Dynamics

Customers respond dynamically to agent actions. Responses vary across steps, introducing uncertainty and requiring adaptive strategies.

---

### SLA Constraints

Each ticket has a limited resolution window. Delays result in penalties and reflect real-world service-level agreements.

---

### Satisfaction and Trust

Two behavioral metrics are tracked:

* **Satisfaction** — short-term response quality
* **Trust Score** — long-term relationship signal

These evolve throughout the episode and directly influence rewards.

---

### Anti-Exploitation Design

The environment penalizes:

* Repetitive or redundant actions
* Premature closure
* Ignoring required escalation
* Inefficient workflows

---

## Tasks and Difficulty

| Level  | Description                                |
| ------ | ------------------------------------------ |
| Easy   | Basic classification and response          |
| Medium | Multi-step handling with SLA awareness     |
| Hard   | Requires escalation and correct sequencing |

---

## Reward Design

The reward function is dense and reflects real operational signals:

### Positive signals

* Correct classification
* Meaningful replies
* Proper escalation
* Successful resolution

### Penalties

* Incorrect classification
* Unnecessary or missing escalation
* SLA violations
* Premature closure

### Additional signals

* Satisfaction impact
* Trust score impact
* Priority handling

A final episode-level grading function outputs a score between 0.0 and 1.0.

---

## Evaluation (Grader)

Each episode is evaluated based on:

* Action correctness
* Workflow completion
* Resolution quality
* Efficiency

The grader is deterministic, context-aware, and produces non-constant scores.

---

## Baseline Agent

A baseline agent is provided to demonstrate expected behavior.

It performs:

* Keyword-based classification
* Rule-based escalation decisions
* Sequential workflow execution

### Run baseline

```bash
python -m scripts.run_baseline
```

---

## Inference (Submission Requirement)

The project includes `inference.py` for evaluation.

It:

* Uses an OpenAI-compatible client
* Reads environment variables:

  * `OPENAI_API_KEY`
  * `API_BASE_URL`
  * `MODEL_NAME`

Outputs structured logs:

```
[START]
[STEP]
[END]
```

---

## Docker Setup

### Build

```bash
docker build -t support-env .
```

### Run

```bash
docker run -p 7860:7860 support-env
```

---

## Deployment

The environment is deployed as a Docker-based Hugging Face Space.

Endpoints:

* `/reset`
* `/step`
* `/state`

Live Space:
https://huggingface.co/spaces/mano678/openenv-support-ai

---

## Project Structure

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
├── inference.py
├── validate-submission.sh
└── README.md
```

---

## OpenEnv Compliance

* step(action)
* reset()
* state()
* Typed models (Pydantic)
* openenv.yaml
* Docker-compatible deployment

---

## Reproducibility

* Deterministic grading
* Stable baseline behavior
* Fully containerized execution

---

## Key Strengths

* Real-world applicability
* Multi-step interaction design
* Strong reward shaping
* Trust and satisfaction modeling
* Resistant to trivial agent exploitation

---

## Limitations

* Simulated customer responses
* No external tool integration
* Domain limited to support workflows

---

## Future Improvements

* Tool usage simulation (e.g., billing APIs)
* Multi-agent workflows (agent + supervisor)
* Expanded ticket dataset
* LLM-based response evaluation

---

## Conclusion

SupportEnv provides a structured and realistic environment for evaluating AI agents in customer support workflows. It combines operational realism with efficient execution, making it suitable for benchmarking and applied research.
