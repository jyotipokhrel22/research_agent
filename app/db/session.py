from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URL)

db = client.research_db

users_collection = db.users
papers_collection = db.papers
reports_collection = db.reports