import json
import random
from env.models import Observation, Action, Reward
from env.reward import compute_reward
from env.graders import grade_episode
from env.tools import process_refund, fix_technical_issue, restore_account
from env.tasks import TASKS


class SupportEnv:
    def __init__(self):
        with open("data/tickets.json") as f:
            self.tickets = json.load(f)

        self.index = 0
        self.state_data = None

    def reset(self):

        # 🔥 SELECT TASK
        task_names = list(TASKS.keys())
        task_name = task_names[self.index % len(task_names)]
        task = TASKS[task_name]

        # 🔥 FILTER TICKETS
        filtered_tickets = [
            t for t in self.tickets
            if t.get("difficulty", "easy") == task["difficulty"]
        ]

        # 🔥 FALLBACK
        if not filtered_tickets:
            filtered_tickets = self.tickets

        # 🔥 FIXED: ALWAYS ASSIGN TICKET OUTSIDE IF
        ticket = filtered_tickets[self.index % len(filtered_tickets)]

        self.index += 1

        # 🔥 FIXED: state_data always initialized
        self.state_data = {
            "task": task_name,
            "ticket": ticket,
            "time_waiting": 0,
            "actions": [],
            "conversation": [],
            "sla_remaining": (3 if ticket["tier"] == "premium" else 5) + random.choice([0, 1]),
            "satisfaction": 1.0,
            "trust_score": 1.0,
            "resolved": False,

            # 🔥 MULTI-AGENT
            "active_agent": "support",
            "agent_history": ["support"],

            # 🔥 NEW: DONE FLAG
            "done": False
        }

        return self._get_observation()


    def step(self, action: Action):

        # 🔥 HARD SAFETY CHECK
        if self.state_data is None:
            raise ValueError("Call reset() before step()")

        # 🔥 HARD STOP AFTER DONE
        if self.state_data.get("done", False):
            return (
                self._get_observation(),
                Reward(score=0.0, reason="Episode already finished"),
                True,
                {}
            )

        ticket = self.state_data["ticket"]

        # 🔹 Compute reward
        score, reason = compute_reward(
            self.state_data,
            action,
            ticket
        )

        actions = self.state_data["actions"]

        # 🔥 EARLY WRONG ACTION PENALTY
        if len(actions) == 0 and action.action_type != "classify":
            score -= 0.3
            reason += " | Must classify first"

        # 🔥 WORKFLOW ORDER ENFORCEMENT
        if action.action_type == "reply" and "classify" not in actions:
            score -= 0.3
            reason += " | Reply before classification"

        if action.action_type == "escalate" and "reply" not in actions:
            score -= 0.2
            reason += " | Escalation before reply"

        if action.action_type == "close" and "reply" not in actions:
            score -= 0.4
            reason += " | Closed without handling"

        # 🔥 NEXT BEST ACTION REWARD
        if len(actions) == 0 and action.action_type == "classify":
            score += 0.2
            reason += " | Good start"

        elif actions == ["classify"] and action.action_type == "reply":
            score += 0.3
            reason += " | Good progression"

        elif actions == ["classify", "reply"] and action.action_type in ["escalate", "close"]:
            score += 0.3
            reason += " | Good decision"

        # 🔥 STRONG LOOP PREVENTION
        if action.action_type in actions:
            score -= 0.3
            reason += f" | Repeated action penalty ({action.action_type})"

        # 🔹 Update state
        self.state_data["actions"].append(action.action_type)
        self.state_data["time_waiting"] += 1

        # 🔥 SLA LOGIC
        self.state_data["sla_remaining"] -= 1
        if self.state_data["sla_remaining"] < 0:
            score -= 0.5
            reason += " | SLA violated"

        # 🔥 CONVERSATION TRACKING
        if action.content:
            self.state_data["conversation"].append(
                f"[{self.state_data['active_agent']}] {action.content}"
            )

        # 🔥 MULTI-AGENT HANDOFF
        if action.action_type == "escalate":
            self.state_data["active_agent"] = "specialist"
            self.state_data["agent_history"].append("specialist")

            specialist_note = f"[SPECIALIST] Handling {ticket['category']} issue"
            self.state_data["conversation"].append(specialist_note)

        # 🔥 SPECIALIST HANDLING
        if action.action_type == "escalate":
            specialist_responses = {
                "technical": "Engineering team has fixed the issue.",
                "billing": "Billing correction has been applied.",
                "account": "Account access has been restored."
            }

            specialist_reply = specialist_responses.get(
                ticket["category"],
                "Issue resolved by specialist team."
            )

            self.state_data["conversation"].append(specialist_reply)
            self.state_data["resolved"] = True

            # 🔥 TOOL SIMULATION
            tool_result = None

            if ticket["category"] == "billing":
                tool_result = process_refund(ticket["id"])
            elif ticket["category"] == "technical":
                tool_result = fix_technical_issue(ticket["id"])
            elif ticket["category"] == "account":
                tool_result = restore_account(ticket["id"])

            if tool_result:
                self.state_data["conversation"].append(
                    f"[SYSTEM] {tool_result['message']}"
                )
                self.state_data["resolved"] = True
                score += 0.3
                reason += " | Tool-assisted resolution"

        # 🔥 DYNAMIC CUSTOMER RESPONSE
        if action.action_type == "reply":
            responses = [
                "This still doesn't solve my issue.",
                "Thanks, but I need more help.",
                "Okay, that makes sense.",
                "This is urgent, please resolve quickly!"
            ]
            customer_reply = random.choice(responses)
            self.state_data["conversation"].append(
                f"[CUSTOMER] {customer_reply}"
            )

        # 🔥 SATISFACTION MODEL
        if action.action_type == "classify":
            self.state_data["satisfaction"] -= 0.05
        elif action.action_type == "reply":
            self.state_data["satisfaction"] += 0.1
        elif action.action_type == "escalate":
            self.state_data["satisfaction"] += 0.2

        # 🔥 TRUST SCORE
        if action.action_type == "reply":
            self.state_data["trust_score"] += 0.05
        elif action.action_type == "escalate":
            self.state_data["trust_score"] += 0.1
        elif action.action_type == "close" and not self.state_data["resolved"]:
            self.state_data["trust_score"] -= 0.4

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

        # 🔥 ANTI-EXPLOIT
        if self.state_data["actions"].count("classify") > 2:
            score -= 0.3
            reason += " | Repeated classification penalty"

        # 🔥 EXTRA STEP PRESSURE
        if self.state_data["time_waiting"] > 4:
            score -= 0.2
            reason += " | Too many steps"

        # 🔥 CLAMP VALUES
        self.state_data["satisfaction"] = max(0.0, min(1.5, self.state_data["satisfaction"]))
        self.state_data["trust_score"] = max(0.0, min(1.5, self.state_data["trust_score"]))

        done = False

        if action.action_type == "close":
            done = True

        if self.state_data["time_waiting"] > 6 or self.state_data["satisfaction"] <= 0:
            done = True

        # 🔹 Final grading
        if done:
            task_name = self.state_data.get("task", "easy_task")
            grader = TASKS[task_name]["grader"]

            final_score = grader(self.state_data["actions"], ticket)

            score = (score * 0.5) + (final_score * 0.5)
            score = max(-1.0, min(score, 1.0))

            reason += f" | Final Score Bonus: {final_score}"

            # 🔥 FIX: mark done
            self.state_data["done"] = True

        return (
            self._get_observation(),
            Reward(score=score, reason=reason),
            done,
            {}
        )

    def state(self):
        return self.state_data

    def _get_observation(self):
        if self.state_data is None:
            raise ValueError("Call reset() first")

        t = self.state_data["ticket"]

        return Observation(
            ticket_id=t["id"],
            customer_message=t["message"],
            customer_tier=t["tier"],
            sentiment=t["sentiment"],
            time_waiting=self.state_data["time_waiting"],
            previous_actions=self.state_data["actions"],
            conversation_history=self.state_data["conversation"],
            sla_remaining=self.state_data["sla_remaining"],
            priority=t.get("priority", "medium"),
            difficulty=t.get("difficulty", "easy"),
            trust_score=self.state_data["trust_score"],
            active_agent=self.state_data["active_agent"]
        )