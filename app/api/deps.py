import uuid

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import User


async def get_db_session() -> AsyncSession:
    async for session in get_db():
        yield session


async def get_current_user(
    session: AsyncSession = Depends(get_db_session),
    x_user_id: str | None = Header(default=None),
) -> User:
    """Very small auth shim.

    If X-User-Id is provided, we load that user.
    Otherwise we create an anonymous user and return it.
    """

    if x_user_id:
        try:
            user_uuid = uuid.UUID(x_user_id)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid X-User-Id header",
            ) from e

        res = await session.execute(select(User).where(User.id == user_uuid))
        user = res.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user

    anon = User(email=f"anon-{uuid.uuid4()}@example.com", name="Anonymous")
    session.add(anon)
    await session.commit()
    await session.refresh(anon)
    return anon
