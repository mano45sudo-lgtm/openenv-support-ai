import json
from env.models import Observation, Action, Reward
from env.reward import compute_reward
from env.graders import grade_episode


class SupportEnv:
    def __init__(self):
        with open("data/tickets.json") as f:
            self.tickets = json.load(f)

        self.index = 0
        self.state_data = None

    def reset(self):
        # cycle through tasks
        ticket = self.tickets[self.index % len(self.tickets)]
        self.index += 1

        self.state_data = {
            "ticket": ticket,
            "time_waiting": 0,
            "actions": []
        }

        return self._get_observation()

    def step(self, action: Action):
        ticket = self.state_data["ticket"]

        # compute step reward
        score, reason = compute_reward(
            self.state_data,
            action,
            ticket["category"]
        )

        # update state
        self.state_data["actions"].append(action.action_type)
        self.state_data["time_waiting"] += 1

        done = False

        # end conditions
        if action.action_type == "close":
            done = True

        if self.state_data["time_waiting"] > 5:
            done = True  # prevent infinite loops

        # final grading
        if done:
            final_score = grade_episode(self.state_data["actions"])
            score += final_score
            reason += f" | Final Score Bonus: {final_score}"

        return (
            self._get_observation(),
            Reward(score=score, reason=reason),
            done,
            {}
        )

    def state(self):
        return self.state_data

    def _get_observation(self):
        t = self.state_data["ticket"]

        return Observation(
            ticket_id=t["id"],
            customer_message=t["message"],
            customer_tier=t["tier"],
            sentiment=t["sentiment"],
            time_waiting=self.state_data["time_waiting"],
            previous_actions=self.state_data["actions"]
        )