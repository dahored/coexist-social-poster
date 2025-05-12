from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles

from routers import x_router, instagram_router, facebook_router, whatsapp_router, telegram_router, post_router
from utils.auth import validate_token  

app = FastAPI(
    title="Social Poster API",
    version="1.0.0",
    dependencies=[Depends(validate_token)] 
)

# Include routers
app.include_router(x_router.router, prefix="/api/v1/x")
app.include_router(instagram_router.router, prefix="/api/v1/instagram")
app.include_router(facebook_router.router, prefix="/api/v1/facebook")
app.include_router(whatsapp_router.router, prefix="/api/v1/whatsapp")
app.include_router(telegram_router.router, prefix="/api/v1/telegram")
app.include_router(post_router.router, prefix="/api/v1/posts")

# Static files
app.mount("/public", StaticFiles(directory="public"), name="public")
