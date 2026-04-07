import os
from typing import List
from openai import OpenAI

from env.environment import SupportEnv
from env.models import Action

# 🔥 REQUIRED ENV VARIABLES
API_BASE_URL = os.getenv("API_BASE_URL") or "https://router.huggingface.co/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or "Qwen/Qwen2.5-72B-Instruct"
HF_TOKEN = os.getenv("HF_TOKEN")

MAX_STEPS = 10
SUCCESS_THRESHOLD = 0.3

# 🔹 Initialize client safely
client = None
if HF_TOKEN:
    try:
        client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
    except Exception:
        client = None

env = SupportEnv()


# ---------------- LOGGING ----------------

def log_start(task: str, env_name: str, model: str):
    print(f"[START] task={task} env={env_name} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: str | None):
    err = error if error else "null"
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={err}",
        flush=True
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True
    )


# ---------------- SAFE LLM ----------------

def safe_llm(message: str):
    if client is None:
        return None

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Classify support ticket."},
                {"role": "user", "content": message}
            ],
            max_tokens=50,
            temperature=0.3
        )
        return (response.choices[0].message.content or "").lower()
    except Exception:
        return None


# ---------------- STRONG POLICY ----------------

def choose_action(obs):
    msg = obs.customer_message.lower()
    actions = obs.previous_actions
    priority = getattr(obs, "priority", "medium")
    difficulty = getattr(obs, "difficulty", "easy")

    # 🔹 STEP 1: CLASSIFY FIRST
    if "classify" not in actions:
        if "charge" in msg or "refund" in msg:
            return Action(action_type="classify", category="billing")
        elif "crash" in msg or "error" in msg:
            return Action(action_type="classify", category="technical")
        elif "account" in msg or "login" in msg:
            return Action(action_type="classify", category="account")
        else:
            return Action(action_type="classify", category="general")

    # 🔹 STEP 2: REPLY
    if "reply" not in actions:
        return Action(action_type="reply", content="We are actively resolving your issue.")

    # 🔹 STEP 3: ESCALATE (SMART)
    if "escalate" not in actions:
        if priority == "critical":
            return Action(action_type="escalate")

        if "crash" in msg or "error" in msg:
            return Action(action_type="escalate")

        if difficulty == "hard":
            return Action(action_type="escalate")

    # 🔹 STEP 4: CLOSE
    if "close" not in actions:
        return Action(action_type="close")

    return Action(action_type="close")


# ---------------- MAIN ----------------

def main():
    rewards = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start("support_task", "support_env", MODEL_NAME)

    try:
        obs = env.reset()
        done = False

        for step in range(1, MAX_STEPS + 1):
            if done:
                break

            steps_taken = step

            # 🔥 ALWAYS USE STRONG POLICY (LLM optional only)
            action = choose_action(obs)

            error = None

            try:
                obs, reward, done, _ = env.step(action)
                r = reward.score
            except Exception as e:
                r = 0.0
                done = True
                error = str(e)

            rewards.append(r)

            log_step(
                step=step,
                action=action.action_type,
                reward=r,
                done=done,
                error=error
            )

        # 🔥 NORMALIZED SCORE
        if rewards:
            raw_score = sum(rewards)
            score = max(0.0, min(raw_score / len(rewards), 1.0))
        else:
            score = 0.0

        success = score >= SUCCESS_THRESHOLD

    finally:
        try:
            env.state()
        except Exception:
            pass

        log_end(success, steps_taken, score, rewards)


if __name__ == "__main__":
    main()