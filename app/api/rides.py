from typing import List

from fastapi import APIRouter, HTTPException

from app.schemas.ride import RideCreateRequest, RideResponse
from app.services.ride_service import ride_service

router = APIRouter(tags=["rides"])


@router.post("/rides", response_model=RideResponse)
def create_ride(payload: RideCreateRequest) -> RideResponse:
    try:
        row = ride_service.create_ride(payload.name)
        return RideResponse(**dict(row))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/rides", response_model=List[RideResponse])
def list_rides() -> List[RideResponse]:
    rows = ride_service.list_rides()
    return [RideResponse(**dict(row)) for row in rows]


@router.delete("/rides/{ride_id}")
def delete_ride(ride_id: int):
    try:
        ride_service.delete_ride(ride_id)
        return {"status": "ok", "message": "Ride session removed"}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))