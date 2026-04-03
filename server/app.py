from fastapi import FastAPI
from pydantic import BaseModel
from env.environment import SupportEnv
from env.models import Action
import uvicorn

app = FastAPI()

# Initialize environment
env = SupportEnv()


# Request model for step
class StepRequest(BaseModel):
    action_type: str
    content: str | None = None
    category: str | None = None


@app.get("/")
def root():
    return {"message": "SupportEnv is running"}


# REQUIRED FOR VALIDATION
@app.post("/reset")
def reset():
    obs = env.reset()
    return {
        "observation": obs.dict()
    }


# STEP ENDPOINT
@app.post("/step")
def step(request: StepRequest):
    action = Action(
        action_type=request.action_type,
        content=request.content,
        category=request.category
    )

    obs, reward, done, _ = env.step(action)

    return {
        "observation": obs.dict(),
        "reward": reward.dict(),
        "done": done
    }


# OPTIONAL: expose state
@app.get("/state")
def state():
    return env.state()


# 🔥 REQUIRED FOR OPENENV VALIDATION
def main():
    uvicorn.run(app, host="0.0.0.0", port=7860)


# 🔥 REQUIRED ENTRY POINT
if __name__ == "__main__":
    main()