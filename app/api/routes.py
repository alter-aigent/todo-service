from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.models import Task, TaskStatus, User
from app.schemas.task import TaskCreate, TaskRead, TaskStatusUpdate, TaskUpdate
from app.schemas.user import UserCreate, UserRead

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db_session)) -> User:
    user = User(email=str(payload.email), name=payload.name)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    db: AsyncSession = Depends(get_db_session),
) -> Task:
    user = await db.get(User, payload.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    task = Task(
        user_id=payload.user_id,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        due_at=payload.due_at,
        status=TaskStatus.pending.value,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.get("/tasks", response_model=list[TaskRead])
async def list_tasks(
    db: AsyncSession = Depends(get_db_session),
    user_id: UUID | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    due_before: datetime | None = Query(default=None),
    due_after: datetime | None = Query(default=None),
    priority: int | None = Query(default=None, ge=0, le=10),
    sort: str = Query(default="-created_at", description="Sort by field, prefix with '-' for desc"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[Task]:
    stmt = select(Task)

    if user_id:
        stmt = stmt.where(Task.user_id == user_id)

    if status_filter:
        stmt = stmt.where(Task.status == status_filter.strip().upper())
    if due_before:
        stmt = stmt.where(Task.due_at.is_not(None)).where(Task.due_at <= due_before)
    if due_after:
        stmt = stmt.where(Task.due_at.is_not(None)).where(Task.due_at >= due_after)
    if priority is not None:
        stmt = stmt.where(Task.priority == priority)

    sort_desc = sort.startswith("-")
    sort_field = sort[1:] if sort_desc else sort
    sort_map = {
        "created_at": Task.created_at,
        "updated_at": Task.updated_at,
        "due_at": Task.due_at,
        "priority": Task.priority,
        "status": Task.status,
        "title": Task.title,
    }
    col = sort_map.get(sort_field)
    if col is None:
        raise HTTPException(status_code=400, detail="Invalid sort field")
    stmt = stmt.order_by(desc(col) if sort_desc else asc(col))

    stmt = stmt.limit(limit).offset(offset)
    res = await db.execute(stmt)
    return list(res.scalars().all())


@router.get("/tasks/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> Task:
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: UUID,
    payload: TaskUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> Task:
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(task, k, v)

    await db.commit()
    await db.refresh(task)
    return task


@router.patch("/tasks/{task_id}/status", response_model=TaskRead)
async def update_task_status(
    task_id: UUID,
    payload: TaskStatusUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> Task:
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = payload.status
    if payload.status in (TaskStatus.done.value, TaskStatus.cancelled.value):
        task.completed_at = datetime.now(timezone.utc)
    else:
        task.completed_at = None

    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> None:
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.delete(task)
    await db.commit()
    return None
