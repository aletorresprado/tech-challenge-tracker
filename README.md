# Tech Challenge Tracker

API REST para organizar desafíos técnicos personales, registrar su dificultad y seguir su progreso. Construida con **Python, FastAPI, Pydantic y Firebase Firestore** como proyecto práctico de aprendizaje de backend y bases de datos NoSQL.

Permite crear, consultar, actualizar y eliminar desafíos. Los datos se guardan en Firestore y permanecen después de reiniciar el servidor.

## Funcionalidades

- CRUD completo con identificadores generados por Firestore.
- Filtro por estado: pendientes, en progreso y completados.
- Actualización parcial con PATCH, conservando los campos no enviados.
- Validación de datos y respuestas HTTP para solicitudes inválidas y recursos inexistentes.
- Documentación interactiva en Swagger UI y esquema OpenAPI.

## Tecnologías

| Tecnología | Uso |
| --- | --- |
| Python | Lenguaje del backend |
| FastAPI | Rutas HTTP, parámetros e inyección de dependencias |
| Pydantic | Modelos y validación de datos |
| Firebase Firestore | Persistencia NoSQL en colecciones y documentos |
| Firebase Admin SDK | Acceso a Firestore desde Python |
| Uvicorn | Servidor ASGI |

## Estructura

```text
tech-challenge-tracker/
├── backend/
│   ├── main.py             # Endpoints
│   ├── models.py           # Modelos de creación, respuesta y actualización
│   ├── database.py         # Inicialización y dependencia de Firestore
│   ├── requirements.txt    # Dependencias
│   └── credentials/        # Clave local; excluida de Git
├── docs/
│   └── aprendizaje.md      # Construcción paso a paso
├── .gitignore
└── README.md
```

## Ejecutar localmente

Necesitás Git, Python 3.10 o superior y un proyecto de Firebase con Firestore. El entorno utilizado durante el desarrollo fue Python 3.13 en Windows.

### 1. Clonar e instalar

En PowerShell:

```powershell
git clone https://github.com/aletorresprado/tech-challenge-tracker.git
cd tech-challenge-tracker/backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Usamos directamente el Python del entorno virtual para evitar instalaciones globales y problemas de activación en PowerShell.

### 2. Configurar Firebase

1. Creá un proyecto en la [consola de Firebase](https://console.firebase.google.com/).
2. Creá una base **Cloud Firestore Standard**, con ID **`(default)`**, elegí su ubicación y seleccioná reglas en modo producción.
3. En **Configuración del proyecto → Cuentas de servicio**, generá una clave privada.
4. Creá la carpeta `backend/credentials` y guardá el JSON como `firebase-service-account.json`.

La clave es privada y no debe subirse a GitHub. La carpeta `backend/credentials/` está excluida mediante `.gitignore`.

### 3. Iniciar el servidor

Desde `backend`, en la misma terminal:

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = (Resolve-Path .\credentials\firebase-service-account.json).Path
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

La variable se configura para esa terminal; repetí la asignación si abrís otra. Detené el servidor con `Ctrl+C`.

- **API:** http://127.0.0.1:8000
- **Swagger UI:** http://127.0.0.1:8000/docs
- **OpenAPI:** http://127.0.0.1:8000/openapi.json

`GET /` comprueba que FastAPI responde. Firestore se utiliza al ejecutar los endpoints de desafíos.

## Endpoints

| Método | Ruta | Operación | Éxito |
| --- | --- | --- | --- |
| GET | `/` | Comprobar que la API responde | 200 |
| POST | `/challenges` | Crear un desafío | 201 |
| GET | `/challenges` | Listar, con filtro opcional `status` | 200 |
| GET | `/challenges/{challenge_id}` | Consultar uno | 200 |
| PATCH | `/challenges/{challenge_id}` | Actualizar campos | 200 |
| DELETE | `/challenges/{challenge_id}` | Eliminar | 204, sin cuerpo |

Las operaciones por ID devuelven **404** si el desafío no existe. Las entradas inválidas devuelven **422**. Sin `GOOGLE_APPLICATION_CREDENTIALS`, los endpoints de desafíos devuelven **503**.

## Ejemplo de uso

En `/docs`, abrí **POST /challenges → Try it out**, enviá este cuerpo y presioná **Execute**:

```json
{
  "title": "Practicar FastAPI",
  "description": "Implementar una API con persistencia NoSQL",
  "difficulty": "medium",
  "status": "pending"
}
```

La respuesta incluye esos campos y un `id` generado por Firestore. Cada desafío es un documento en la colección `challenges`; su identificador se devuelve como `id` en la API.

| Campo | Restricciones | Predeterminado |
| --- | --- | --- |
| `title` | Obligatorio al crear; entre 1 y 120 caracteres | — |
| `description` | Hasta 2000 caracteres | `""` |
| `difficulty` | `easy`, `medium`, `hard` | `easy` |
| `status` | `pending`, `in_progress`, `completed` | `pending` |

Copiá el ID recibido y usalo en **PATCH /challenges/{challenge_id}** con:

```json
{"status": "in_progress"}
```

Solo se modifica el estado. PATCH rechaza cuerpos vacíos, valores `null` y campos desconocidos, incluido `id`.

Consultá luego:

```text
GET /challenges?status=in_progress
```

El filtro se ejecuta en Firestore. Sin `status` se listan todos; si no hay coincidencias, se devuelve `200` con `[]`.

## Validación

Se probaron manualmente desde Swagger UI la creación, consulta, actualización y eliminación contra Firestore, los errores 404 y la persistencia después de reiniciar el servidor. Durante el desarrollo también se verificaron casos de validación y operaciones con Firestore simulado. El repositorio todavía no incluye una suite de pruebas automatizadas.

Para repetir el flujo: creá un desafío, consultalo por ID, cambiá su estado, reiniciá el servidor y comprobá que siga guardado. Finalmente, eliminá el desafío de prueba y verificá que consultarlo devuelva 404.

## Estado actual y próximos pasos

Backend funcional para aprendizaje y ejecución local. Todavía no incluye interfaz web, autenticación, paginación ni despliegue público de la API. Firebase Admin utiliza permisos IAM de la cuenta de servicio y no las reglas de seguridad de los clientes web; falta incorporar autenticación y autorización antes de exponer datos de usuarios.

- [ ] Filtro por dificultad y fechas de creación.
- [ ] Paginación e índices para consultas más avanzadas.
- [ ] Separación de rutas y acceso a datos.
- [ ] Pruebas automatizadas.
- [ ] Autenticación con Firebase y desafíos por usuario.
- [ ] Interfaz web y despliegue.

## Aprendizaje

El proyecto practica diseño de endpoints REST, parámetros de ruta y consulta, códigos HTTP, validación con Pydantic, inyección de dependencias y modelado mediante documentos NoSQL.

El [recorrido paso a paso](docs/aprendizaje.md) conserva las etapas de construcción, incluida la primera versión con almacenamiento en memoria.

**Autor:** [aletorresprado](https://github.com/aletorresprado).
