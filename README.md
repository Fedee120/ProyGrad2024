# ProyGrad2024

El siguiente README.md describe los pasos para hacer el setup del entorno para correr el proyecto en modo desarrollo (local) y producción (docker).

A destacar, ambos modos usan diferentes puertos para poder correr ambos modos a la vez sin cambiar nada, para lograr esto se usan variables de entorno para configurar los puertos de cada servicio, en local (.env-template files) se usan 8090 y 8091 los cuales son especificados en main.py (backend) y package.json (frontend), mientras que en docker (docker-compose.yml) se usan 8080 y 8081 los cuales son especificados en los respectivos Dockerfiles (+ nginx.conf en el caso de frontend). Tambien no importa si se quiere correr en desarrollo o en producción, es necesario levantar el docker para que Milvus esté corriendo.

## Para correr el proyecto

### Configurar el entorno para desarrollo

Revisar el archivo `README.md` de la carpeta backend y frontend para ver como levantar el entorno de desarrollo para cada uno. En particular, es necesario configurar untracked secrets.

### Levantar el docker que tiene la db, el backend y el frontend

```console
docker-compose up --build
```

### Cargar base de datos

Ir a la carpeta backend y correr python3 -m data.load_data

### Abrir el frontend

Abrir el link http://localhost:8081 que deberia estar levantado el frontend para interactuar
