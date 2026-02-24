from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from backend.utils.logger import setup_logger

# Import the chat_routes module to access the shared `rag_retriever` and setter
from backend.api import chat_router as _unused  # ensure package import
from backend.api.chat_routes import rag_retriever, set_rag

logger = setup_logger(__name__)
router = APIRouter()

class ParamsUpdate(BaseModel):
    params: Dict[str, Any]

class ValidateRequest(BaseModel):
    sample_size: Optional[int] = 200
    top_k: Optional[int] = None

@router.get("/rag/params")
async def get_params():
    if not rag_retriever:
        raise HTTPException(status_code=404, detail="RAG retriever not initialized")
    if hasattr(rag_retriever, 'get_params'):
        return rag_retriever.get_params()
    # fallback: return some basic info
    return { 'type': type(rag_retriever).__name__ }

@router.post("/rag/params")
async def update_params(body: ParamsUpdate):
    if not rag_retriever:
        raise HTTPException(status_code=404, detail="RAG retriever not initialized")
    if hasattr(rag_retriever, 'update_params'):
        try:
            rag_retriever.update_params(**body.params)
            return { 'status': 'ok', 'updated': body.params }
        except Exception as e:
            logger.error(f"Failed to update params: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail="Retriever does not support parameter updates")

@router.post("/rag/build-index")
async def build_index():
    if not rag_retriever:
        raise HTTPException(status_code=404, detail="RAG retriever not initialized")
    try:
        rag_retriever.build_index()
        return { 'status': 'index_built' }
    except Exception as e:
        logger.error(f"Index build failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rag/validate")
async def validate(req: ValidateRequest):
    if not rag_retriever:
        raise HTTPException(status_code=404, detail="RAG retriever not initialized")
    if hasattr(rag_retriever, 'validate'):
        try:
            result = rag_retriever.validate(sample_size=req.sample_size, top_k=req.top_k)
            return { 'status': 'ok', 'result': result }
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail="Retriever does not support validation")
