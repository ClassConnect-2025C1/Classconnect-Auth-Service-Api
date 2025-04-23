## 📁 Estructura del proyecto

Este proyecto sigue la arquitectura de packing by layer. A continuación se detalla la estructura del código y el propósito de cada carpeta:

├── alembic/           # Migraciones de base de datos con Alembic
├── controller/        # Contiene los **controladores** de la aplicación. Aquí se definen los endpoints que responden a las solicitudes HTTP, delegando la lógica de negocio a los servicios.
├── dbConfig/          # Configuración de la base de datos (conexión, sesión)
├── externals/         # Integraciones externas (por ejemplo las notificacions)
├── models/            # Contiene los **modelos de base de datos** definidos utilizando SQLAlchemy
├── repositories/      # Operaciones CRUD y acceso a datos
├── routes/            # Definición de rutas de la API (FastAPI routers)
├── schemas/           # Contiene los modelos de datos utilizados para validar y estructurar las **requests** y **responses** de la API
├── services/          # Lógica de negocio principal
├── tests/             # Pruebas unitarias e integración
└── utils/             # Funciones utilitarias (security con las funcionalidad para encriptar y desencriptar los tokens)

