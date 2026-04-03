from pydantic import BaseModel
from typing import List, Optional

class Observation(BaseModel):
    ticket_id: str
    customer_message: str
    customer_tier: str
    sentiment: str
    time_waiting: int
    previous_actions: List[str]

class Action(BaseModel):
    action_type: str  # classify, reply, escalate, close
    content: Optional[str] = None
    category: Optional[str] = None

class Reward(BaseModel):
    score: float
    reason: str