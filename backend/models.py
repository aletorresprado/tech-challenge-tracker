from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ChallengeStatus = Literal["pending", "in_progress", "completed"]


class ChallengeCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)
    difficulty: Literal["easy", "medium", "hard"] = "easy"
    status: ChallengeStatus = "pending"


class Challenge(ChallengeCreate):
    id: str


class ChallengeUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    difficulty: Literal["easy", "medium", "hard"] | None = None
    status: ChallengeStatus | None = None

    @model_validator(mode="after")
    def validate_changes(self) -> "ChallengeUpdate":
        if not self.model_fields_set:
            raise ValueError("Enviá al menos un campo para actualizar")
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("Los campos enviados no pueden ser null")
        return self
