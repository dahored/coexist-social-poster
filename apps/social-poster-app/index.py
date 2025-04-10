import asyncio
from modules.twitter import TwitterAPI

async def runPosts():
    """Ejecuta las publicaciones en Twitter"""
    twitter_api = TwitterAPI()
    await twitter_api.run_posts()  # ✅ Se usa await correctamente

# Ejecutar si el script es ejecutado directamente
if __name__ == "__main__":
    asyncio.run(runPosts())  # ✅ Se ejecuta correctamente en el event loop
