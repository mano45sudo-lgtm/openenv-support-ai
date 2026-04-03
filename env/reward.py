def compute_reward(state, action, correct_category):
    score = 0.0
    reasons = []

    if action.category:
        if action.category == correct_category:
            score += 0.3
            reasons.append("Correct classification")
        else:
            score -= 0.2
            reasons.append("Wrong classification")

    if action.action_type == "reply":
        score += 0.2
        reasons.append("Replied")

    if action.action_type == "escalate" and correct_category == "technical":
        score += 0.3
        reasons.append("Correct escalation")

    if action.action_type == "close":
        score += 0.2
        reasons.append("Closed ticket")

    if state["time_waiting"] > 2:
        score -= 0.1
        reasons.append("Delay penalty")

    return score, ", ".join(reasons)