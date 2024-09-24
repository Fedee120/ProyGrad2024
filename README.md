# ProyGrad2024

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
```

### Levantar el docker que tiene la db y el backend

```console
docker-compose up --build
```

### Cargar base de datos

Ir a la carpeta backend y correr python3 -m eval.evaluate_rag_qa luego de modificar la variable de ese script de load a true temporalmente

### Correr el prototipo

```console
streamlit run frontend/streamlit_app.py
```