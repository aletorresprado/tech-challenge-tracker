from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from google.api_core.exceptions import NotFound
from google.cloud.firestore import Client
from google.cloud.firestore_v1.base_query import FieldFilter

from database import get_db
from models import Challenge, ChallengeCreate, ChallengeStatus, ChallengeUpdate

app = FastAPI(title="Tech Challenge Tracker")

Database = Annotated[Client, Depends(get_db)]


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Tech Challenge Tracker está funcionando"}


@app.post("/challenges", response_model=Challenge, status_code=status.HTTP_201_CREATED)
def create_challenge(data: ChallengeCreate, db: Database) -> Challenge:
    document = db.collection("challenges").document()
    document.set(data.model_dump())
    challenge = Challenge(id=document.id, **data.model_dump())
    return challenge


@app.delete(
    "/challenges/{challenge_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    responses={404: {"description": "Desafío no encontrado"}},
)
def delete_challenge(challenge_id: str, db: Database) -> Response:
    reference = db.collection("challenges").document(challenge_id)
    document = reference.get()
    if not document.exists:
        raise HTTPException(status_code=404, detail="Desafío no encontrado")

    reference.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/challenges", response_model=list[Challenge])
def list_challenges(
    db: Database,
    status: Annotated[
        ChallengeStatus | None, Query(description="Filtrar desafíos por estado")
    ] = None,
) -> list[Challenge]:
    query = db.collection("challenges")
    if status is not None:
        query = query.where(filter=FieldFilter("status", "==", status))
    documents = query.stream()
    return [Challenge(**{**document.to_dict(), "id": document.id}) for document in documents]


@app.get(
    "/challenges/{challenge_id}",
    response_model=Challenge,
    responses={404: {"description": "Desafío no encontrado"}},
)
def get_challenge(challenge_id: str, db: Database) -> Challenge:
    document = db.collection("challenges").document(challenge_id).get()
    if not document.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Desafío no encontrado",
        )
    return Challenge(**{**document.to_dict(), "id": document.id})


@app.patch(
    "/challenges/{challenge_id}",
    response_model=Challenge,
    responses={404: {"description": "Desafío no encontrado"}},
)
def update_challenge(
    challenge_id: str, data: ChallengeUpdate, db: Database
) -> Challenge:
    reference = db.collection("challenges").document(challenge_id)
    document = reference.get()
    if not document.exists:
        raise HTTPException(status_code=404, detail="Desafío no encontrado")

    changes = data.model_dump(exclude_unset=True)
    challenge = Challenge(**{**document.to_dict(), **changes, "id": document.id})
    try:
        reference.update(changes)
    except NotFound as error:
        # El documento pudo eliminarse entre la lectura y la actualización.
        raise HTTPException(status_code=404, detail="Desafío no encontrado") from error
    return challenge
