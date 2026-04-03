def grade_episode(actions):
    score = 0.0

    if "classify" in actions:
        score += 0.3
    if "reply" in actions:
        score += 0.3
    if "close" in actions:
        score += 0.4

    return min(score, 1.0)