[![codecov](https://codecov.io/gh/ClassConnect-2025C1/Classconnect-Auth-Service-Api/graph/badge.svg?token=ZOGrg23W6e)](https://codecov.io/gh/ClassConnect-2025C1/Classconnect-Auth-Service-Api)

[![Python Package without Conda](https://github.com/ClassConnect-2025C1/Classconnect-Auth-Service-Api/actions/workflows/python-package-conda.yml/badge.svg)](https://github.com/ClassConnect-2025C1/Classconnect-Auth-Service-Api/actions/workflows/python-package-conda.yml)

## 📁 Estructura del proyecto

Este proyecto sigue la arquitectura *package by layer*, donde cada carpeta agrupa archivos según su responsabilidad dentro del sistema. A continuación se detalla la estructura y propósito de cada componente:

- **`alembic/`**  
  Contiene las migraciones de base de datos generadas con Alembic.

- **`controller/`**  
  Define los controladores de la aplicación. Aquí se crean los endpoints de la API y se delega la lógica de negocio a los servicios.

- **`dbConfig/`**  
  Configuración de la base de datos, incluyendo la conexión y sesión de SQLAlchemy.

- **`externals/`**  
  Módulos de integración con servicios externos, como por ejemplo el envío de notificaciones.

- **`models/`**  
  Modelos de base de datos definidos con SQLAlchemy, que representan las tablas y sus columnas.

- **`repositories/`**  
  Encapsula el acceso a datos y operaciones CRUD sobre los modelos.

- **`routes/`**  
  Agrupa los routers de FastAPI, permitiendo modularizar y registrar las rutas en la app principal.

- **`schemas/`**  
  Esquemas de validación de datos usando Pydantic, usados para estructurar `requests` y `responses`.

- **`services/`**  
  Contiene la lógica de negocio principal. Los controladores llaman a estas funciones para ejecutar las acciones deseadas.

- **`tests/`**  
  Pruebas unitarias y de integración para asegurar el correcto funcionamiento del sistema.

- **`utils/`**  
  Funciones auxiliares como encriptación, manejo de tokens u otras herramientas reutilizables.

## 🛠️ Instalación y uso

### Requisitos previos

- Docker
- Docker Compose

### Ejecución local del proyecto

Pararse en el root del proyecto y ejecutar el siguiente comando:

```bash
docker compose up --env-file .env.development up --build
```
