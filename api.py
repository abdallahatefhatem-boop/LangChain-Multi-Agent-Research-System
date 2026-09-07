from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.pipeline.pipeline import run_research_pipeline

app = FastAPI(
    title="LangChain Multi-Agent Research API",
    description="API for running the multi-agent research pipeline.",
    version="1.0.0"
)

class ResearchRequest(BaseModel):
    topic: str

class ResearchResponse(BaseModel):
    report: str
    feedback: str
    search_results: str
    scraped_content: str

@app.post("/research", response_model=ResearchResponse)
async def research_topic(request: ResearchRequest):
    """
    Executes the multi-agent research pipeline for a given topic.
    """
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")
        
    try:
        # Run the pipeline (this is synchronous; in a heavy production setting, 
        # consider running this in a background task or thread pool).
        result = run_research_pipeline(request.topic)
        
        return ResearchResponse(
            report=result.get("report", ""),
            feedback=result.get("feedback", ""),
            search_results=result.get("search_results", ""),
            scraped_content=result.get("scraped_content", "")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
