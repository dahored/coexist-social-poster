import asyncio
from modules.x import XAPI

async def runPosts():
    """Executes posts on X"""
    x_api = XAPI()
    await x_api.run_posts()  # ✅ Await is used correctly

# Run if the script is executed directly
if __name__ == "__main__":
    asyncio.run(runPosts())  # ✅ Correctly executed within the event loop