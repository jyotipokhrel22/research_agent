from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from app.models.paper import Paper
from app.db.session import papers_collection

router = APIRouter()

def validate_object_id(id_str: str, label: str = "ID") -> ObjectId:
    if not ObjectId.is_valid(id_str):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"'{id_str}' is not a valid {label} format",
        )
    return ObjectId(id_str)

async def get_paper_or_404(paper_id: str) -> dict:
    oid = validate_object_id(paper_id, "Paper ID")
    paper = await papers_collection.find_one({"_id": oid})
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper with id '{paper_id}' not found",
        )
    paper["_id"] = str(paper["_id"])
    return paper

@router.post("/papers", status_code=status.HTTP_201_CREATED)
async def create_paper(paper: Paper):
    new_paper = await papers_collection.insert_one(paper.dict())
    return {
        "message": "Paper added successfully",
        "id": str(new_paper.inserted_id),
    }

@router.get("/papers", status_code=status.HTTP_200_OK)
async def get_papers():
    papers = []
    async for p in papers_collection.find():
        p["_id"] = str(p["_id"])
        papers.append(p)
    return papers

@router.get("/papers/{paper_id}", status_code=status.HTTP_200_OK)
async def get_paper(paper_id: str):
    return await get_paper_or_404(paper_id)

@router.put("/papers/{paper_id}", status_code=status.HTTP_200_OK)
async def update_paper(paper_id: str, paper: Paper):
    oid = validate_object_id(paper_id, "Paper ID")
    result = await papers_collection.update_one(
        {"_id": oid}, {"$set": paper.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper with id '{paper_id}' not found",
        )
    return {"message": "Paper updated successfully"}

@router.delete("/papers/{paper_id}", status_code=status.HTTP_200_OK)
async def delete_paper(paper_id: str):
    oid = validate_object_id(paper_id, "Paper ID")
    result = await papers_collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper with id '{paper_id}' not found",
        )
    return {"message": "Paper deleted successfully"}