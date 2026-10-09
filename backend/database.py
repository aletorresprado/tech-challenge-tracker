import os
from functools import lru_cache

import firebase_admin
from fastapi import HTTPException
from firebase_admin import firestore
from google.cloud.firestore import Client


@lru_cache
def get_db() -> Client:
    # Este tutorial usa una cuenta de servicio mediante esta variable.
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        raise HTTPException(
            status_code=503,
            detail="Configurá GOOGLE_APPLICATION_CREDENTIALS y reiniciá el servidor.",
        )

    try:
        firebase_app = firebase_admin.get_app()
    except ValueError:
        firebase_app = firebase_admin.initialize_app()

    return firestore.client(app=firebase_app)
