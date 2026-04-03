import os
from openai import OpenAI
from env.environment import SupportEnv
from env.models import Action

# 🔥 REQUIRED ENV VARIABLES
API_BASE_URL = os.getenv("API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
HF_TOKEN = os.getenv("HF_TOKEN")

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)

env = SupportEnv()


def log_start(task, env_name, model):
    print(f"[START] task={task} env={env_name} model={model}", flush=True)


def log_step(step, action, reward, done):
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error=null",
        flush=True
    )


def log_end(success, steps, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} rewards={rewards_str}",
        flush=True
    )


def main():
    obs = env.reset()
    done = False
    step = 0
    rewards = []

    log_start("support_task", "support_env", MODEL_NAME)

    while not done and step < 10:
        step += 1

        message = obs.customer_message

        # 🔥 REQUIRED: OpenAI client usage
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Classify support ticket."},
                {"role": "user", "content": message}
            ]
        )

        text = response.choices[0].message.content.lower()

        # Simple mapping
        if "charge" in text:
            action = Action(action_type="classify", category="billing")
        elif "crash" in text:
            action = Action(action_type="classify", category="technical")
        else:
            action = Action(action_type="reply", content="We are resolving your issue.")

        obs, reward, done, _ = env.step(action)

        rewards.append(reward.score)
        log_step(step, action.action_type, reward.score, done)

    success = sum(rewards) > 0.5
    log_end(success, step, rewards)


if __name__ == "__main__":
    main()