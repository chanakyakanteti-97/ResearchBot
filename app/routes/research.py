from fastapi import APIRouter, HTTPException
from app.core.agent import run_research_agent
from app.schemas import ResearchRequest, ResearchResponse

router = APIRouter()


@router.post("/research", response_model=ResearchResponse)
def research(request: ResearchRequest):
    """Run the AI agent to research a topic and return a full report."""

    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Research topic cannot be empty.")

    if len(request.topic) > 300:
        raise HTTPException(status_code=400, detail="Topic too long. Keep it under 300 characters.")

    try:
        print(f"\n[ResearchBot] Starting research: {request.topic}")
        result = run_research_agent(request.topic)

        return ResearchResponse(
            topic=request.topic,
            report=result["report"],
            steps=result["steps"],
            total_steps=len(result["steps"])
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@router.get("/health")
def health():
    return {"status": "ResearchBot agent is ready ✅"}
