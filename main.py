from fastapi import FastAPI
from routers import x_router
from routers import post_router

app = FastAPI(
    title="Social Poster API",
    version="1.0.0"
)

# Include routers
app.include_router(x_router.router, prefix="/api/v1/x")
app.include_router(post_router.router, prefix="/api/v1/posts")