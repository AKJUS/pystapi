from datetime import timedelta

from geojson_pydantic import Feature, Point
from pydantic import AwareDatetime, BaseModel, Field, field_validator, model_validator

from stat_fastapi.models.opportunity import (
    OpportunitySearch,
    OpportunitySearchProperties,
)


class Satellite(BaseModel):
    tle: str
    block_time: tuple[timedelta, timedelta]

    @field_validator("tle")
    @classmethod
    def validate_tle(cls, v: str) -> str:
        lines = [line for line in v.split("\n") if line.strip() != ""]

        if len(lines) != 3:
            raise ValueError("TLE must be 3 lines")

        return v

    @property
    def tle_lines(self) -> tuple[str, str, str]:
        return self.tle.split("\n")


class PassProperties(BaseModel):
    datetime: AwareDatetime
    start: AwareDatetime
    end: AwareDatetime
    view_off_nadir: float = Field(..., alias="view:off_nadir")
    view_azimuth: float = Field(..., alias="view:azimuth")
    view_elevation: float = Field(..., alias="view:elevation")
    sun_elevation: float = Field(..., alias="sun:elevation")
    sun_azimuth: float = Field(..., alias="sun:azimuth")


class Pass(Feature[Point, PassProperties]):
    pass


class OffNadirRange(BaseModel):
    minimum: float = Field(ge=0.0, le=45)
    maximum: float = Field(ge=0.0, le=45)

    @model_validator(mode="after")
    def validate(self) -> "OffNadirRange":
        diff = self.maximum - self.minimum
        if diff < 5.0:
            raise ValueError("range must be at least 5°")
        return self


class Constraints(OpportunitySearchProperties):
    off_nadir: OffNadirRange = OffNadirRange(minimum=0.0, maximum=30.0)


class ValidatedOpportunitySearch(OpportunitySearch):
    properties: Constraints
