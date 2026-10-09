# Tech Challenge Tracker

Proyecto para aprender FastAPI, Pydantic y Firestore paso a paso.

## Paso 1: servidor básico

Desde la raíz del proyecto, en PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Si PowerShell bloquea la activación, podés usar el Python del entorno directamente:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Abrí http://127.0.0.1:8000 para comprobar la respuesta del servidor y
http://127.0.0.1:8000/docs para explorar la documentación interactiva.
Detené el servidor con Ctrl+C.

FastAPI define los endpoints; Uvicorn ejecuta el servidor; Pydantic validará los
datos de los desafíos; firebase-admin permitirá acceder a Firestore.
En este paso no se inicializa Firebase ni se necesitan credenciales.

## Paso 2: modelos y endpoints

`backend/models.py` define los datos con Pydantic. `ChallengeCreate` representa
los datos recibidos y `Challenge` agrega el identificador generado por el servidor.

En http://127.0.0.1:8000/docs, probá `POST /challenges` con:

```json
{
  "title": "Practicar FastAPI",
  "description": "Crear y listar desafíos con validación",
  "difficulty": "easy",
  "status": "pending"
}
```

Luego ejecutá `GET /challenges` para ver el desafío creado. Un título vacío o una
dificultad fuera de `easy`, `medium`, `hard` produce una respuesta 422.

Los datos viven en memoria: se pierden al detener o reiniciar el servidor,
incluidos los reinicios automáticos de `--reload`. Usá un solo proceso en este
paso. El Paso 3 reemplaza esta lista por Firestore.

## Paso 3: persistencia en Firestore

El código actual usa Firestore; el Paso 2 describe la versión anterior en memoria.

1. Creá un proyecto en https://console.firebase.google.com/.
2. En Firestore Database creá una base de datos Standard con ID `(default)`.
   Elegí una ubicación adecuada y reglas en modo producción.
3. En Configuración del proyecto > Cuentas de servicio generá una clave privada.
4. Guardá el JSON como `backend/credentials/firebase-service-account.json`.
   Esta carpeta está excluida de Git. No compartas la clave privada.
5. Detené el servidor con Ctrl+C. Desde `backend`, en PowerShell, ejecutá:

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = (Resolve-Path .\credentials\firebase-service-account.json).Path
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

La variable se configura para esa terminal; repetí la asignación al abrir otra.
`GET /` comprueba que FastAPI está funcionando, no la conexión a Firestore.
Sin la variable, los endpoints de desafíos responden 503 con una indicación.

Creá un desafío desde `/docs`, consultá `GET /challenges`, reiniciá el servidor y
consultá nuevamente. Verificá el documento en la colección `challenges` de la
consola de Firebase. Los desafíos de la versión en memoria no se migran.

Firestore organiza los datos en colecciones y documentos. Cada desafío es un
documento cuyos campos se guardan con `set`; `stream` consulta la colección.
El identificador del documento se devuelve como `id` en nuestra API.

Firebase Admin usa permisos de la cuenta de servicio (IAM), no las reglas de
seguridad de clientes web. Esta API todavía no tiene autenticación: ejecutala
localmente mientras aprendemos.

## Paso 4: consultar un desafío por ID

`GET /challenges/{challenge_id}` consulta un documento concreto de Firestore.
FastAPI toma el ID de la URL y lo entrega al parámetro `challenge_id`.

1. Ejecutá `GET /challenges` en `/docs` y copiá el `id` de un desafío.
2. En `GET /challenges/{challenge_id}`, pulsá **Try it out**, pegá ese ID y
   ejecutá la consulta. Deberías recibir 200 y un único desafío.
3. Repetí con `id-que-no-existe`. Deberías recibir 404 con
   `{"detail": "Desafío no encontrado"}`.

`HTTPException` interrumpe el endpoint y permite devolver el código HTTP y
el mensaje del error. Un documento inexistente es un 404, no una lista vacía.

## Paso 5: actualizar algunos campos

`PATCH /challenges/{challenge_id}` recibe un `ChallengeUpdate`: los campos
se pueden omitir, pero los enviados deben ser válidos y no pueden ser `null`.
Se rechazan cuerpos vacíos y campos desconocidos (incluido `id`) con 422.

En `/docs`, copiá el ID de un desafío y probá el PATCH con:

```json
{"status": "completed"}
```

La respuesta 200 contiene el desafío actualizado. Consultalo nuevamente con
GET para comprobar que el estado quedó guardado y los otros campos se conservaron.
Un ID inexistente devuelve 404; `{"status": "invalid"}` devuelve 422.

`model_dump(exclude_unset=True)` incluye solo los campos enviados.
Firestore `update` modifica esos campos sin reemplazar el documento completo.

## Paso 6: eliminar un desafío

`DELETE /challenges/{challenge_id}` elimina el documento de Firestore.
Si existe, devuelve 204 sin cuerpo; si no existe, devuelve 404.

1. Creá con POST un desafío de prueba, por ejemplo `{"title": "Prueba de borrado"}`.
2. Copiá su ID y ejecutá DELETE desde `/docs` con ese identificador.
3. Comprobá el 204 y consultá ese ID con GET: ahora debería devolver 404.
4. Consultá la lista: los otros desafíos deberían seguir presentes.
5. Repetí el DELETE con el mismo ID: debería devolver 404.

La comprobación de existencia es necesaria porque `delete()` de Firestore
también permite eliminar una referencia cuyo documento ya no existe.

## Paso 7: filtrar por estado

`GET /challenges` acepta el parámetro de consulta opcional `status`:

- `/challenges`: todos los desafíos.
- `/challenges?status=in_progress`: solo los que están en progreso.
- `/challenges?status=completed`: solo los completados.
- `/challenges?status=pending`: solo los pendientes.

En `/docs`, recargá la página, abrí GET /challenges y pulsá **Try it out**.
Elegí un estado y ejecutá. Para consultar todos, omití el parámetro (no envíes
un texto vacío). También podés abrir esas URLs directamente en el navegador.

Un estado inválido devuelve 422. Si el estado es válido pero no tiene
coincidencias, la respuesta es 200 con `[]`.

`ChallengeStatus` centraliza los estados permitidos en los modelos y el filtro.
`Query` documenta el parámetro; Firestore ejecuta la consulta con
`where(filter=FieldFilter("status", "==", status))` antes de devolver documentos.
Referencia: https://firebase.google.com/docs/firestore/query-data/queries
