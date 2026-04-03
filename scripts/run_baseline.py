from env.environment import SupportEnv
from env.models import Action

env = SupportEnv()
obs = env.reset()

done = False
total_score = 0

while not done:
    msg = obs.customer_message.lower()

    # STEP 1 — CLASSIFY
    if "classify" not in obs.previous_actions:
        if any(word in msg for word in ["charge", "charged", "refund", "billing", "payment"]):
            action = Action(action_type="classify", category="billing")

        elif any(word in msg for word in ["crash", "error", "bug", "issue"]):
            action = Action(action_type="classify", category="technical")

        else:
            action = Action(action_type="classify", category="general")

    # STEP 2 — ESCALATE (ONLY FOR TECHNICAL)
    elif "technical" in msg and "escalate" not in obs.previous_actions:
        action = Action(action_type="escalate")

    # STEP 3 — REPLY (ONLY ONCE)
    elif "reply" not in obs.previous_actions:
        action = Action(action_type="reply", content="We are resolving your issue.")

    # STEP 4 — CLOSE (FORCE EXIT)
    else:
        action = Action(action_type="close")

    obs, reward, done, _ = env.step(action)
    total_score += reward.score

    print("Step Reward:", reward)

print("Final Score:", total_score)