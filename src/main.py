from fastapi import FastAPI
from models import Base
from database import engine
from api.v1.endpoints.users import router as api_router_users
from api.v1.endpoints.short_urls import router as api_router_short_urls
from api.v1.endpoints.without_prefix import router as api_router_without_prefix
from middlewares.pydantic_errors import validation_pydantic_field
from middlewares.catcher import CatcherExceptionsMiddleware
from api.endpoints import router as index_router
from settings import settings
from fastapi import FastAPI
from middlewares.catcher import CatcherExceptionsMiddleware
from middlewares.pydantic_errors import validation_pydantic_field
from fastapi.middleware import Middleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.version,
    middleware=[
        Middleware(CatcherExceptionsMiddleware)
    ]
)


app.include_router(index_router)
app.include_router(api_router_users, prefix="/v1", tags=["Users"])
app.include_router(api_router_short_urls,prefix="/v1", tags=["Short URLs"])
app.include_router(api_router_without_prefix, tags=["Without Prefix"])


validation_pydantic_field(app)