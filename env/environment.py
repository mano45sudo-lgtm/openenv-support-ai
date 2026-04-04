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
        ticket = self.tickets[self.index % len(self.tickets)]
        self.index += 1

        self.state_data = {
            "ticket": ticket,
            "time_waiting": 0,
            "actions": [],
            "conversation": [],
            "sla_remaining": 3 if ticket["tier"] == "premium" else 5,
            "satisfaction": 1.0
        }

        return self._get_observation()

    def step(self, action: Action):
        ticket = self.state_data["ticket"]

        # 🔹 Compute reward
        score, reason = compute_reward(
            self.state_data,
            action,
            ticket
        )

        # 🔹 Update actions
        self.state_data["actions"].append(action.action_type)
        self.state_data["time_waiting"] += 1

        # 🔥 SLA LOGIC
        self.state_data["sla_remaining"] -= 1
        if self.state_data["sla_remaining"] < 0:
            score -= 0.5
            reason += " | SLA violated"

        # 🔥 CONVERSATION TRACKING
        if action.content:
            self.state_data["conversation"].append(action.content)

        # 🔥 SATISFACTION MODEL
        if action.action_type == "classify":
            self.state_data["satisfaction"] -= 0.05
        elif action.action_type == "reply":
            self.state_data["satisfaction"] += 0.1
        elif action.action_type == "escalate":
            self.state_data["satisfaction"] += 0.2

        # clamp satisfaction
        self.state_data["satisfaction"] = max(0.0, min(1.5, self.state_data["satisfaction"]))

        done = False

        # 🔹 End conditions
        if action.action_type == "close":
            done = True

        if self.state_data["time_waiting"] > 6:
            done = True  # prevent infinite loops

        # 🔹 Final grading
        if done:
            final_score = grade_episode(self.state_data["actions"], ticket)
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
            previous_actions=self.state_data["actions"],

            # 🔥 NEW REAL-WORLD FEATURES
            conversation_history=self.state_data["conversation"],
            sla_remaining=self.state_data["sla_remaining"],
            priority=t.get("priority", "medium"),
            difficulty=t.get("difficulty", "easy")
        )