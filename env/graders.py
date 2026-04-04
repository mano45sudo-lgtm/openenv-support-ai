def grade_episode(actions, ticket):
    score = 0.0
    correct_category = ticket["category"]
    priority = ticket.get("priority", "medium")
    difficulty = ticket.get("difficulty", "easy")

    # 🔹 1. Classification must happen early
    if "classify" in actions:
        if actions.index("classify") == 0:
            score += 0.3
        else:
            score += 0.1  # late classification = weaker

    # 🔹 2. Escalation logic
    if correct_category == "technical":
        if "escalate" in actions:
            score += 0.25
        else:
            score -= 0.2  # missed escalation
    else:
        if "escalate" not in actions:
            score += 0.15
        else:
            score -= 0.1  # unnecessary escalation

    # 🔹 3. Reply quality
    if "reply" in actions:
        score += 0.2
    else:
        score -= 0.2  # no response = bad

    # 🔹 4. Closing behavior (must be last)
    if "close" in actions:
        if actions[-1] == "close":
            score += 0.2
        else:
            score -= 0.2  # closing too early

    # 🔹 5. Efficiency (penalize long sequences)
    if len(actions) <= 3:
        score += 0.1
    elif len(actions) > 5:
        score -= 0.2

    # 🔹 6. Priority handling (NEW 🔥)
    if priority == "critical":
        if "escalate" in actions:
            score += 0.2
        else:
            score -= 0.3

    # 🔹 7. Difficulty bonus (NEW 🔥)
    if difficulty == "hard":
        score += 0.1

    return max(0.0, min(score, 1.0))