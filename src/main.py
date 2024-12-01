from fastapi import FastAPI
from models import Base
from database import engine
from api.v1.endpoints.users import router as api_router_users
from api.v1.endpoints.short_urls import router as api_router_short_urls
from api.v1.endpoints.without_prefix import router as api_router_without_prefix
from api.endpoints import router as index_router
from settings import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.project_name,
    version=settings.version
)

app.include_router(index_router)
app.include_router(api_router_users, prefix="/v1", tags=["Users"])
app.include_router(api_router_short_urls,prefix="/v1", tags=["Short URLs"])
app.include_router(api_router_without_prefix, tags=["Without Prefix"])