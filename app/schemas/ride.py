from pydantic import BaseModel, Field


class RideCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)


class RideResponse(BaseModel):
    id: int
    name: str
    slug: str
    ride_date: str
    archive_path: str
    status: str
    created_at: str
    updated_at: str