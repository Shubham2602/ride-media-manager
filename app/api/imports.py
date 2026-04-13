from typing import List

from fastapi import APIRouter, HTTPException

from app.schemas.import_job import ImportCreateRequest, ImportJobResponse
from app.schemas.media_file import MediaFileResponse
from app.services.import_service import import_service

router = APIRouter(tags=["imports"])


@router.post("/imports", response_model=ImportJobResponse)
def create_import(payload: ImportCreateRequest) -> ImportJobResponse:
    try:
        row = import_service.create_import_job(
            ride_session_id=payload.ride_session_id,
            device_id=payload.device_id,
        )
        return ImportJobResponse(**dict(row))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/imports/{job_id}/start", response_model=ImportJobResponse)
def start_import(job_id: int) -> ImportJobResponse:
    try:
        row = import_service.start_import(job_id)
        return ImportJobResponse(**dict(row))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/imports/{job_id}", response_model=ImportJobResponse)
def get_import(job_id: int) -> ImportJobResponse:
    try:
        row = import_service.get_job(job_id)
        return ImportJobResponse(**dict(row))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/imports/{job_id}/files", response_model=List[MediaFileResponse])
def list_import_files(job_id: int) -> List[MediaFileResponse]:
    try:
        rows = import_service.list_job_files(job_id)
        return [MediaFileResponse(**dict(row)) for row in rows]
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))