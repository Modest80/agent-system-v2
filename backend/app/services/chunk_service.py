from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import Chunk


async def list_chunks_by_document(
    session: AsyncSession,
    document_id: UUID,
    limit: int = 200,
    offset: int = 0,
) -> List[Chunk]:
    stmt = (
        select(Chunk)
        .where(Chunk.document_id == document_id)
        .order_by(Chunk.chunk_index.asc())
        .offset(offset)
        .limit(limit)
    )
    res = await session.execute(stmt)
    return list(res.scalars().all())


async def get_chunk(session: AsyncSession, chunk_id: UUID) -> Optional[Chunk]:
    stmt = select(Chunk).where(Chunk.id == chunk_id)
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


async def create_chunks_bulk(
    session: AsyncSession,
    document_id: UUID,
    chunks: List[dict],
) -> List[Chunk]:
    # chunks: list of dicts with chunk_index/text/embedding/chunk_metadata
    entities: List[Chunk] = []
    for c in chunks:
        entities.append(
            Chunk(
                document_id=document_id,
                chunk_index=c["chunk_index"],
                text=c["text"],
                embedding=c.get("embedding"),
                chunk_metadata=c.get("chunk_metadata"),
            )
        )
    session.add_all(entities)
    await session.commit()
    for e in entities:
        await session.refresh(e)
    return entities


async def update_chunk_metadata(
    session: AsyncSession,
    chunk_id: UUID,
    chunk_metadata: dict,
) -> Optional[Chunk]:
    chunk = await get_chunk(session, chunk_id)
    if not chunk:
        return None
    chunk.chunk_metadata = chunk_metadata
    await session.commit()
    await session.refresh(chunk)
    return chunk


async def delete_chunk(session: AsyncSession, chunk_id: UUID) -> bool:
    stmt = delete(Chunk).where(Chunk.id == chunk_id)
    res = await session.execute(stmt)
    await session.commit()
    return res.rowcount > 0


async def delete_chunks_by_document(session: AsyncSession, document_id: UUID) -> int:
    stmt = delete(Chunk).where(Chunk.document_id == document_id)
    res = await session.execute(stmt)
    await session.commit()
    return int(res.rowcount or 0)


async def search_chunks_by_embedding(
    session: AsyncSession,
    embedding: list[float],
    top_k: int = 5,
    document_id: Optional[UUID] = None,
):
    # cosine distance: меньше = ближе
    distance = Chunk.embedding.cosine_distance(embedding)

    stmt = select(Chunk, distance.label("distance")).where(Chunk.embedding.is_not(None))
    if document_id:
        stmt = stmt.where(Chunk.document_id == document_id)

    stmt = stmt.order_by(distance.asc()).limit(top_k)

    res = await session.execute(stmt)
    return [{"chunk": row[0], "distance": float(row[1])} for row in res.all()]
