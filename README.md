# ProyGrad2024
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

El siguiente README.md describe los pasos para hacer el setup del entorno para correr el proyecto en modo desarrollo (local) y producción (docker). Además de especificar como personalizar el corpuse usado o el dominio restringido del chatbot.

A destacar, ambos modos usan diferentes puertos para poder correr ambos modos a la vez sin cambiar nada, para lograr esto se usan variables de entorno para configurar los puertos de cada servicio, en local (.env-template files) se usan 8090 y 8091 los cuales son especificados en main.py (backend) y package.json (frontend), mientras que en docker (docker-compose.yml) se usan 8080 y 8081 los cuales son especificados en los respectivos Dockerfiles (+ nginx.conf en el caso de frontend). Tambien no importa si se quiere correr en desarrollo o en producción, es necesario levantar el docker para que Milvus esté corriendo.

## Para correr el proyecto

### Configurar el entorno para desarrollo

Revisar el archivo `README.md` de la carpeta backend y frontend para ver como levantar el entorno de desarrollo para cada uno. En particular, es necesario configurar untracked secrets.

### Levantar el docker que tiene la db, el backend y el frontend

```console
docker-compose up --build
```

### Cargar base de datos

Ir a la carpeta backend y correr `python3 -m data.load_data` con el entorno de desarrollo configurado

### Abrir el frontend

Abrir el link http://localhost:8081 que deberia estar levantado el frontend para interactuar

## Para personalizar el corpus usado o el dominio restringido del chatbot

### Personalización del corpus
Para que el chatbot pase a responder en base a otro corpus de documentos, se precisa actualizar los que se encuentren en la carpeta `backend/data/raw/` previo a realizar el paso de "Cargar base de datos" especificado en la sección anterior. Preferiblemente se debe asegurar que los archivos tengan nombres descriptivos.

### Personalización del dominio restringido
Para que el chatbot pase de responder sobre **Inteligencia Artificial** a otro dominio (por ejemplo, **Cocina**), basta con actualizar los prompts de sistema de los LLMs contenidos en los siguientes archivos; se indica exactamente qué fragmento debes reemplazar:

| Archivo                                                   | Fragmento a editar                                                                                                                                                                                                                                        | Acción                                                                                             |
| --------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `backend/agent/router.py`                                 | **`system_prompt_text`** del *Router* – reglas de decisión: <br>• `'retrieve'` cuando la consulta “involucra AI o educación” → reemplazar por “involucra cocina”.<br>• `'deny'` cuando “no está relacionada a AI” → poner “no está relacionada a cocina”. | Esta es la lógica que hace que niegue todo lo externo; actualízala con el nuevo tema.              |
| `backend/agent/llms/conversational_response_generator.py` | **`system_prompt_text`** – primera linea (“You are a conversational assistant designed to help people who are curious about generative artificial intelligence…”).                                                 | Sustituye cada mención de IA por tu nuevo dominio.                  |
| `backend/agent/llms/pedagogical_response_generator.py`    | **`system_prompt_text`** – primera línea idéntica a la anterior.                                                                                                                                                                                          | Igual que arriba: redefinir el campo temático.                                                     |
| `backend/agent/llms/deny_response_generator.py`           | **Bloque `system_prompt_text` completo** | Reemplaza **todas** las menciones a “artificial intelligence”, “AI”, “education” y derivados por tu nuevo dominio (p. ej. “cocina”, “gastronomía”). Mantén la estructura de cortesía y la lógica de negar preguntas fuera de tema. |
| `backend/agent/llms/no_retrieval_response_generator.py`   | **Bloque `system_prompt_text` completo** | Igualmente, busca y reemplaza todas las referencias temáticas (incluido el nombre del bot “Aprende IA”) por el nuevo dominio. Asegúrate de que la parte que describe al chatbot y sus fuentes quede coherente.                     |

Con esto el backend quedará especializado al nuevo dominio y seguirá rechazando cualquier pregunta que no se relacione con él. _Cabe destactar que seguramente también resulte necesario actualizar el corpus siguiendo el punto anterior dado que consultas de información tienen que ser basadas en las fuentes curadas y el corpus actual esta centrado en el dominio restringido actual_.
