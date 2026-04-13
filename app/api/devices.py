from typing import List

from fastapi import APIRouter, HTTPException

from app.schemas.device import DeviceResponse, ScanResult
from app.services.device_service import device_service
from app.services.media_scanner import scanner_service

router = APIRouter(tags=["devices"])


@router.get("/devices", response_model=List[DeviceResponse])
def list_devices() -> List[DeviceResponse]:
    try:
        rows = device_service.list_devices()
        return [DeviceResponse(**dict(row)) for row in rows]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/devices/{device_id}/scan", response_model=ScanResult)
def scan_device(device_id: int) -> ScanResult:
    try:
        return scanner_service.scan_device(device_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))