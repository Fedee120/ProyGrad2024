# ProyGrad2024

El siguiente README.md describe los pasos para levantar el proyecto en modo desarrollo (local) y producción (docker). 

A destacar, ambos modos usan diferentes puertos para poder correr ambos modos a la vez sin cambiar nada, para lograr esto se usan variables de entorno para configurar los puertos de cada servicio, en local (.env-template files) se usan 8090 y 8091, mientras que en docker (docker-compose.yml) se usan 8080 y 8081. Tambien no importa si se quiere correr localmente o en docker, es necesario levantar el docker para que Milvus esté corriendo.

Antes de hacer nada, es necesario configurar los archivos `.env` en la carpeta backend y frontend con las variables de entorno necesarias para que los servicios funcionen. Para esto seguir los `.env.template` correspondientes.


## Para correr el proyecto

### Levantar el docker que tiene la db, el backend y el frontend

```console
docker-compose up --build
```

### Cargar base de datos

Ir a la carpeta backend y correr python3 -m eval.evaluate_rag_qa luego de modificar la variable de ese script de load a true temporalmente

### Abrir el frontend

Abrir el link http://localhost:8081 que deberia estar levantado el frontend para interactuar



## Para configurar el entorno para desarrollar

### BACKEND

#### Crear un entorno virtual (parados en el directorio del repositorio)

```console
python3 -m venv proygrad_venv
```

#### Activar el entorno virtual

```console
source proygrad_venv/bin/activate
```

*Este comando ejecuta el script activate que se encuentra en el directorio bin dentro del entorno virtual. El script configura el entorno de shell actual para usar los paquetes y la configuración del entorno virtual. Realiza varios cambios como modificar la variable de entorno PATH, modificar el prompt del shell (la parte que se muestra antes de que escribas un comando) para indicar que estás en un entorno virtual, entre otras cosas.*

Para desactivar el entorno virtual correr: 
```console
deactivate
```

#### Instalar los paquetes Python requeridos para el proyecto

```console
pip3 install -r backend/requirements.txt
```

#### Correr el backend

```console
python3 backend/main.py
```

#### Verificar que el backend esté funcionando

Abrir el link http://localhost:8090/check_status (va a fallar porque se requeire autenticación)


### FRONTEND

#### Instalar los paquetes Node.js requeridos para el proyecto

```console
npm install
```

#### Correr el frontend

```console
npm start
```

#### Verificar que el frontend esté funcionando

Abrir el link http://localhost:8091
