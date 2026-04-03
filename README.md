---
title: OpenEnv Support AI
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Support Triage OpenEnv

## Overview
This environment simulates a real-world customer support system where an AI agent must:
- Classify tickets
- Respond appropriately
- Escalate issues if needed
- Close tickets

## Tasks
1. Classification (Easy)
2. Resolution (Medium)
3. Full Lifecycle (Hard)

## Observation Space
- ticket_id
- customer_message
- customer_tier
- sentiment
- time_waiting
- previous_actions

## Action Space
- classify
- reply
- escalate
- close

## Reward Design
- +0.3 correct classification
- +0.2 reply
- +0.3 correct escalation
- +0.2 close
- -0.1 delay penalty

## Run Locally
python -m scripts.run_baseline

## Docker
docker build -t support-env .
docker run support-env

## Example Output
Step Reward: ...
Final Score: ...