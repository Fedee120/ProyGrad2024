# ProyGrad2024


## Para correr el proyecto

### Configurar .env

Crear `.env` dentro de la carpeta backend siguiendo el `.env.template` dentro de la carpeta backend y pedir las claves para que los servicios funcionen

### Levantar el docker que tiene la db, el backend y el fronted

```console
docker-compose up --build
```

### Cargar base de datos

Ir a la carpeta backend y correr python3 -m eval.evaluate_rag_qa luego de modificar la variable de ese script de load a true temporalmente

### Abrir el frontend

Abrir el link http://localhost:8501 que deberia estar levantado el front para interactuar


## Para configurar el entorno para desarrollar

### Crear un entorno virtual (parados en el directorio del repositorio)

```console
python3 -m venv proygrad_venv
```

### Activar el entorno virtual

```console
source proygrad_venv/bin/activate
```

*Este comando ejecuta el script activate que se encuentra en el directorio bin dentro del entorno virtual. El script configura el entorno de shell actual para usar los paquetes y la configuración del entorno virtual. Realiza varios cambios como modificar la variable de entorno PATH, modificar el prompt del shell (la parte que se muestra antes de que escribas un comando) para indicar que estás en un entorno virtual, entre otras cosas.*

Para desactivar el entorno virtual correr: 
```console
deactivate
```

### Instalar los paquetes Python requeridos para el proyecto

```console
pip3 install -r frontend/requirements.txt
pip3 install -r backend/requirements.txt
```