import uuid

from fastapi import Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import User


async def get_db_session() -> AsyncSession:
    async for s in get_db():
        return s
    raise RuntimeError("DB session generator did not yield")


async def get_current_user(
    db: AsyncSession,
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    x_user_email: str | None = Header(default=None, alias="X-User-Email"),
) -> User:
    """Very simple auth stub.

    - If X-User-Id is provided, user is loaded/created with that UUID.
    - Else if X-User-Email is provided, user is loaded/created by email.

    This keeps the service self-contained while still enforcing per-user ownership.
    """

    if not x_user_id and not x_user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Provide X-User-Id or X-User-Email header",
        )

    if x_user_id:
        try:
            user_id = uuid.UUID(x_user_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail="Invalid X-User-Id") from e

        user = await db.get(User, user_id)
        if user is None:
            email = x_user_email or f"user-{user_id}@local"
            user = User(id=user_id, email=email)
            db.add(user)
            await db.commit()
            await db.refresh(user)
        return user

    # email path
    stmt = select(User).where(User.email == x_user_email)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    if user is None:
        user = User(email=x_user_email)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user
