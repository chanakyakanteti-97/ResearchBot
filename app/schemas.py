from pydantic import BaseModel

class ResearchRequest(BaseModel):
    topic: str

class AgentStep(BaseModel):
    type: str        # "thought", "tool_call", "tool_result", "final"
    content: str
    tool_name: str | None = None
    tool_args: dict | None = None

class ResearchResponse(BaseModel):
    topic: str
    report: str
    steps: list[AgentStep]
    total_steps: int
