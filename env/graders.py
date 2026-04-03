def grade_episode(actions, ticket):
    score = 0.0
    correct_category = ticket["category"]

    # classification
    if "classify" in actions:
        score += 0.2

    # escalation correctness
    if correct_category == "technical":
        if "escalate" in actions:
            score += 0.3
    else:
        if "escalate" not in actions:
            score += 0.2

    # reply
    if "reply" in actions:
        score += 0.2

    # close
    if "close" in actions:
        score += 0.3

    return min(score, 1.0)