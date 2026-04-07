from env.graders import grade_episode

# 🔥 DEFINE TASKS (MANDATORY)

TASKS = {
    "easy_task": {
        "description": "Classify and reply to a simple customer query",
        "difficulty": "easy",
        "grader": grade_episode
    },

    "medium_task": {
        "description": "Handle ticket with correct classification and possible escalation",
        "difficulty": "medium",
        "grader": grade_episode
    },

    "hard_task": {
        "description": "Handle complex issue with SLA, escalation, and correct workflow",
        "difficulty": "hard",
        "grader": grade_episode
    }
}

