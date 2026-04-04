import json
import random
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
            "sla_remaining": (3 if ticket["tier"] == "premium" else 5) + random.choice([0, 1]),
            "satisfaction": 1.0,
            "resolved": False
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

        # 🔥 DYNAMIC CUSTOMER RESPONSE
        if action.action_type == "reply":
            responses = [
                "This still doesn't solve my issue.",
                "Thanks, but I need more help.",
                "Okay, that makes sense.",
                "This is urgent, please resolve quickly!"
            ]
            customer_reply = random.choice(responses)
            self.state_data["conversation"].append(customer_reply)

        # 🔥 SATISFACTION MODEL
        if action.action_type == "classify":
            self.state_data["satisfaction"] -= 0.05
        elif action.action_type == "reply":
            self.state_data["satisfaction"] += 0.1
        elif action.action_type == "escalate":
            self.state_data["satisfaction"] += 0.2

        # 🔥 ACTION CONSEQUENCES
        if action.action_type == "classify" and action.category != ticket["category"]:
            self.state_data["satisfaction"] -= 0.2

        if action.action_type == "close" and "reply" not in self.state_data["actions"]:
            self.state_data["satisfaction"] -= 0.3

        # 🔥 RESOLUTION LOGIC
        if action.action_type == "reply" and ticket["category"] in ["billing", "general"]:
            self.state_data["resolved"] = True

        if action.action_type == "close" and not self.state_data["resolved"]:
            score -= 0.3
            reason += " | Closed without resolution"

        # 🔥 ANTI-EXPLOIT (loop detection)
        if self.state_data["actions"].count("classify") > 2:
            score -= 0.3
            reason += " | Repeated classification penalty"

        # clamp satisfaction
        self.state_data["satisfaction"] = max(0.0, min(1.5, self.state_data["satisfaction"]))

        done = False

        # 🔹 End conditions
        if action.action_type == "close":
            done = True

        if self.state_data["time_waiting"] > 6 or self.state_data["satisfaction"] <= 0:
            done = True  # prevent loops / unhappy user

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

            # 🔥 Enhanced observation
            conversation_history=self.state_data["conversation"],
            sla_remaining=self.state_data["sla_remaining"],
            priority=t.get("priority", "medium"),
            difficulty=t.get("difficulty", "easy")
        )