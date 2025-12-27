from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.chunk import (
    ChunkRead,
    ChunkBulkCreate,
    ChunkMetadataUpdate,
    ChunkSearchRequest,
    ChunkSearchResponse,
    ChunkSearchHit,
)
from app.services.chunk_service import (
    list_chunks_by_document,
    get_chunk,
    create_chunks_bulk,
    update_chunk_metadata,
    delete_chunk,
    search_chunks_by_embedding,
)

from app.database import get_async_session  # проверь название функции


router = APIRouter(prefix="/chunks", tags=["Chunks - Фрагменты"])


@router.get("/document/{document_id}", response_model=list[ChunkRead])
async def api_list_chunks(
    document_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    return await list_chunks_by_document(session, document_id)


@router.post("/document/{document_id}", response_model=list[ChunkRead], status_code=status.HTTP_201_CREATED)
async def api_create_chunks_bulk(
    document_id: UUID,
    payload: ChunkBulkCreate,
    session: AsyncSession = Depends(get_async_session),
):
    chunks_dicts = [c.model_dump() for c in payload.chunks]
    return await create_chunks_bulk(session, document_id, chunks_dicts)


@router.get("/{chunk_id}", response_model=ChunkRead)
async def api_get_chunk(
    chunk_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    chunk = await get_chunk(session, chunk_id)
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return chunk


@router.patch("/{chunk_id}/metadata", response_model=ChunkRead)
async def api_update_chunk_metadata(
    chunk_id: UUID,
    payload: ChunkMetadataUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    chunk = await update_chunk_metadata(session, chunk_id, payload.chunk_metadata)
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return chunk


@router.delete("/{chunk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def api_delete_chunk(
    chunk_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    ok = await delete_chunk(session, chunk_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return None


@router.post("/search", response_model=ChunkSearchResponse)
async def api_search_chunks(
    payload: ChunkSearchRequest,
    session: AsyncSession = Depends(get_async_session),
):
    hits = await search_chunks_by_embedding(
        session=session,
        embedding=payload.embedding,
        top_k=payload.top_k,
        document_id=payload.document_id,
    )
    return ChunkSearchResponse(
        hits=[ChunkSearchHit(chunk=h["chunk"], distance=h["distance"]) for h in hits]
    )
