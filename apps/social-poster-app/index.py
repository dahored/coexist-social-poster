import asyncio
from modules.twitter import TwitterAPI

async def runPosts():
    """Executes posts on Twitter"""
    twitter_api = TwitterAPI()
    await twitter_api.run_posts()  # ✅ Await is used correctly

# Run if the script is executed directly
if __name__ == "__main__":
    asyncio.run(runPosts())  # ✅ Correctly executed within the event loop