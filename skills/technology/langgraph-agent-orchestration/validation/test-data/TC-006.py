# api/routers/risk_router.py
# VIOLATION: Directly importing graph assembly/compiled_graph into API layer bypassing agents/services/
from fastapi import APIRouter
from agents.graphs.risk.graph import compiled_graph  # API Seam Access violation

router = APIRouter()

@router.post("/evaluate")
async def evaluate_risk(payload: dict):
    return await compiled_graph.ainvoke(payload)
