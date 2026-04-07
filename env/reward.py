def compute_reward(state, action, ticket):
    score = 0.0
    reasons = []

    correct_category = ticket["category"]
    priority = ticket.get("priority", "medium")

    # 🔹 1. Classification quality
    if action.category:
        if action.category == correct_category:
            score += 0.3
            reasons.append("Correct classification")
        else:
            score -= 0.2
            reasons.append("Wrong classification")

    # 🔹 2. Reply quality
    if action.action_type == "reply":
        score += 0.2
        reasons.append("Replied")

    # 🔹 3. Escalation logic
    if action.action_type == "escalate":
        if correct_category == "technical":
            score += 0.3
            reasons.append("Correct escalation")
        else:
            score -= 0.1
            reasons.append("Unnecessary escalation")

    # 🔹 4. Closing logic
    if action.action_type == "close":
        if state["resolved"]:
            score += 0.3
            reasons.append("Closed after resolution")
        elif "reply" in state["actions"]:
            score += 0.1
            reasons.append("Closed after partial handling")
        else:
            score -= 0.3
            reasons.append("Premature close")

    # 🔹 5. SLA pressure
    if state["sla_remaining"] <= 0:
        score -= 0.5
        reasons.append("SLA violated")

    # 🔹 6. Delay penalty
    if state["time_waiting"] > 3:
        score -= 0.1
        reasons.append("Delay penalty")

    # 🔹 7. Customer satisfaction
    score += state["satisfaction"] * 0.2
    reasons.append("Satisfaction impact")

    # 🔥 8. TRUST SCORE (NEW — VERY IMPORTANT)
    score += state["trust_score"] * 0.2
    reasons.append("Trust impact")

    # 🔹 9. Priority handling
    if priority == "critical" and action.action_type != "escalate":
        score -= 0.2
        reasons.append("Missed critical escalation")

    # 🔹 10. Resolution bonus (NEW)
    if state["resolved"]:
        score += 0.2
        reasons.append("Issue resolved")
        
    score = max(-1.0, min(score, 1.0))

    return score, ", ".join(reasons)