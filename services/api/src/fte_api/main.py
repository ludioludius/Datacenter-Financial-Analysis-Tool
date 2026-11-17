from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Request, Response, status
from pydantic import BaseModel
from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError

from fte_core.db import get_engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # One engine (and connection pool) for the whole process.
    app.state.engine = get_engine()
    yield
    app.state.engine.dispose()


app = FastAPI(title="Filing Thesis Engine API", version="0.1.0", lifespan=lifespan)


def db_engine(request: Request) -> Engine:
    return request.app.state.engine


class Health(BaseModel):
    status: str
    database: str


@app.get("/health")
def health(engine: Annotated[Engine, Depends(db_engine)], response: Response) -> Health:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except SQLAlchemyError:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return Health(status="error", database="unreachable")
    return Health(status="ok", database="ok")
