# Study Tracker

Aplicación para registrar y analizar el tiempo dedicado al estudio. El proyecto está en desarrollo; actualmente incluye una interfaz web y una API conectadas a PostgreSQL.

## Funcionalidades actuales

- Iniciar, pausar, reanudar y finalizar sesiones de estudio, o registrar sesiones manualmente.
- Organizar el estudio por materias y submaterias.
- Consultar un panel con tiempo estudiado, sesiones recientes y materias con más actividad.
- Revisar el historial con filtros por materia y período, vista individual o agrupada por día, semana o mes.
- Editar y eliminar sesiones, materias y submaterias.

## Tecnologías

- **Frontend:** React, Vite y React Router.
- **Backend:** Python 3.13+, FastAPI, SQLAlchemy y Alembic.
- **Base de datos:** PostgreSQL.

## Inicio local

Necesitas Python 3.13+, [uv](https://docs.astral.sh/uv/), Node.js con npm y Docker Compose.

1. Crea los archivos de entorno a partir de los ejemplos: `.env.example` en la raíz y `frontend/.env.example` en `frontend/`. Ajusta los valores si hace falta.
2. Desde la raíz del proyecto, instala las dependencias y levanta PostgreSQL:

   ```bash
   uv sync
   docker compose up -d
   ```

3. Aplica las migraciones y arranca la API:

   ```bash
   uv run alembic upgrade head
   uv run uvicorn study_tracker.main:app --reload
   ```

   La API y su documentación interactiva estarán en `http://localhost:8000` y `http://localhost:8000/docs`.

4. En otra terminal, instala las dependencias del frontend y arráncalo:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   Vite mostrará la dirección local de la aplicación. La URL de la API se configura con `VITE_API_BASE_URL` en `frontend/.env`.

## Pruebas

Desde la raíz del proyecto:

```bash
uv run pytest
```
