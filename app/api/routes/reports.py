from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from app.models.report import Report
from app.db.session import reports_collection

router = APIRouter()

def validate_object_id(id_str: str, label: str = "ID") -> ObjectId:
    if not ObjectId.is_valid(id_str):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"'{id_str}' is not a valid {label} format",
        )
    return ObjectId(id_str)

async def get_report_or_404(report_id: str) -> dict:
    oid = validate_object_id(report_id, "Report ID")
    report = await reports_collection.find_one({"_id": oid})
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with id '{report_id}' not found",
        )
    report["_id"] = str(report["_id"])
    return report

@router.post("/reports", status_code=status.HTTP_201_CREATED)
async def create_report(report: Report):
    new_report = await reports_collection.insert_one(report.dict())
    return {
        "message": "Report added successfully",
        "id": str(new_report.inserted_id),
    }

@router.get("/reports", status_code=status.HTTP_200_OK)
async def get_reports():
    reports = []
    async for r in reports_collection.find():
        r["_id"] = str(r["_id"])
        reports.append(r)
    return reports

@router.get("/reports/{report_id}", status_code=status.HTTP_200_OK)
async def get_report(report_id: str):
    return await get_report_or_404(report_id)

@router.put("/reports/{report_id}", status_code=status.HTTP_200_OK)
async def update_report(report_id: str, report: Report):
    oid = validate_object_id(report_id, "Report ID")
    updated = await reports_collection.update_one(
        {"_id": oid}, {"$set": report.dict()}
    )
    if updated.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with id '{report_id}' not found",
        )
    return {"message": "Report updated successfully"}

@router.delete("/reports/{report_id}", status_code=status.HTTP_200_OK)
async def delete_report(report_id: str):
    oid = validate_object_id(report_id, "Report ID")
    deleted = await reports_collection.delete_one({"_id": oid})
    if deleted.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with id '{report_id}' not found",
        )
    return {"message": "Report deleted successfully"}