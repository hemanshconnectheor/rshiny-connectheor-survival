import logging
from fastapi import FastAPI, HTTPException, Request     # ← Request added here
from pydantic import BaseModel, Field
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
app = FastAPI(
    title="Integration API",
    description="Endpoints Testing"
)

snapshots = {}   
plots = {}       
llm_responses = {} 



class SnapshotData(BaseModel):
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]

class PlotData(BaseModel):
    plot_url: str                   
    caption: str = ""
    description: str = ""
    metadata: Dict[str, Any] = {}

class QueryData(BaseModel):
    query: str


@app.post("/snapshot/{session_id}/{snapshot_id}")
async def post_snapshot(session_id: str, snapshot_id: str, data: SnapshotData, request: Request):
    raw = await request.body()                     # bytes
    logging.info("RAW /snapshot BODY = %s", raw.decode())
    # -----------------------------------------------------------------

    logging.info("[SNAPSHOT] session_id=%s snapshot_id=%s", session_id, snapshot_id)
    logging.info("Inputs  : %s", data.inputs)
    logging.info("Outputs : %s", data.outputs)
    snapshots[(session_id, snapshot_id)] = data.model_dump()


    return {
        "status": "success",
        "session_id": session_id,
        "snapshot_id": snapshot_id
    }

@app.post("/plot/{session_id}/{snapshot_id}/{plot_id}")
def post_plot(session_id: str, snapshot_id: str, plot_id: str, data: PlotData):

    plots[(session_id, snapshot_id, plot_id)] = data.model_dump()
    logging.info("Outputs : %s", plots)
    return {
        "status": "success",
        "session_id": session_id,
        "snapshot_id": snapshot_id,
        "plot_id": plot_id
    }


@app.post("/ask/{session_id}/{snapshot_id}")
def ask_llm(session_id: str, snapshot_id: str, data: QueryData):

    mock_response = f"LLM processed query: {data.query}"

    llm_responses[(session_id, snapshot_id)] = {
        "query": data.query,
        "response": mock_response
    }
    return {
        "status": "success",
        "session_id": session_id,
        "snapshot_id": snapshot_id,
        "response": mock_response
    }

@app.get("/response/{session_id}/{snapshot_id}")
def get_llm_response(session_id: str, snapshot_id: str):

    # result = llm_responses.get((session_id, snapshot_id))
    response = "Hello Akash How are you?"
    # if not response:
    #     raise HTTPException(status_code=404, detail="No LLM response found for this session/snapshot.")
    return {
        "session_id": session_id,
        "snapshot_id": snapshot_id,
        "response": response
    }
 

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "total_snapshots": len(snapshots),
        "total_plots": len(plots),
        "total_llm_responses": len(llm_responses)
    }


@app.get("/")
def root():
    return {
        "message": "R Shiny + LLM Analysis API. Visit /docs for interactive API documentation."
    }


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
