from env.environment import SupportEnv
from env.models import Action

env = SupportEnv()
obs = env.reset()

done = False
total_score = 0

while not done:
    msg = obs.customer_message.lower()

    # step 1: classify
    if "charged" in msg and "classify" not in obs.previous_actions:
        action = Action(action_type="classify", category="billing")

    # step 2: respond
    elif "reply" not in obs.previous_actions:
        action = Action(action_type="reply", content="We are checking your issue")

    # step 3: close
    else:
        action = Action(action_type="close")

    obs, reward, done, _ = env.step(action)
    total_score += reward.score

    print("Step Reward:", reward)

print("Final Score:", total_score)