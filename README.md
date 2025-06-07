# ProyGrad2024
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Este archivo README.md describe los pasos para configurar el entorno necesario para correr el proyecto tanto en modo desarrollo local como en producción mediante Docker. También especifica cómo personalizar el corpus utilizado por el chatbot y adaptar su dominio temático restringido a otros contextos.

A destacar, el entorno de desarrollo local y el entorno de producción están configurados para utilizar diferentes puertos, permitiendo correr ambos modos a la vez. Para lograr esto, se usan variables de entorno para configurar los puertos de cada servicio.

- Entorno de dessarrollo local

  Utiliza los puertos 8090 (backend) y 8091 (frontend), definidos en los archivos .env-template, y especificados en main.py (backend) y package.json (frontend).
  
- Entorno de producción con Docker

  Utiliza los puertos 8080 (backend) y 8081 (frontend), configurados en los respectivos Dockerfile, y en el archivo nginx.conf (para el frontend).

*Nota:* Independientemente del entorno elegido (desarrollo o producción), es necesario levantar Docker para que Milvus esté disponible y en funcionamiento.


## Ejecución del proyecto

### 1. Modo desarrollo (local)

Revisar los archivos `README.md` dentro de las carpetas `backend` y `frontend` para ver como levantar el entorno de desarrollo para cada uno. En particular, es necesario configurar los untracked secrets.

*Requisito:* Tener Milvus corriendo (ver sección siguiente para levantar con Docker).

Una vez todo esté levantado, el frontend estará disponible en:
http://localhost:8091.

### 2. Modo producción (Docker)
Este modo levanta toda la aplicación (base de datos, backend y frontend) usando contenedores.

```console
docker-compose up --build
```

Una vez todo esté levantado, el frontend estará disponible en:
http://localhost:8081.

## Carga de la base de datos

Una vez configurado el entorno (desarrollo o producción), es necesario poblar la base vectorial con los documentos curados. Para esto, ir a la carpeta `backend` y ejecutar:
```console
python3 -m data.load_data
```

## Personalización del corpus y del dominio temático del chatbot

### Personalización del corpus

Para que el chatbot pase a responder en base a otro corpus de documentos, es necesario reemplazar los archivos que se encuentran en la carpeta `backend/data/raw/` previo a realizar el paso de *"Carga de la base de datos"* especificado anteriormente. Los archivos deben estar en formato PDF y, preferentemente, tener nombres descriptivos que reflejen su contenido.

### Personalización del dominio temático

Para que el chatbot pase de responder sobre **Inteligencia Artificial** a otro dominio (por ejemplo, **Cocina**), basta con actualizar los prompts de sistema de los LLMs definidos en los siguientes archivos, reemplazando los fragmentos indicados con el nuevo enfoque temático.

| Archivo                                                   | Fragmento a editar                                                                                                                                                                                                                                       | Acción                                                                                               |
| --------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `backend/agent/router.py`                                 | **`system_prompt_text`** – Reglas de decisión: <br>• `'retrieve'`: “when the user's query involves AI or education”.<br>• `'deny'`: “when the user's query is not related to AI”. | Actualizá estas reglas con el nuevo dominio. Por ejemplo: <br>• `'retrieve'`: “when the user's query involves cooking”.<br>• `'deny'`: “when the user's query is not related to cooking”.              |
| `backend/agent/llms/conversational_response_generator.py` | **`system_prompt_text`** - Primera línea (“You are a conversational assistant designed to help people who are curious about generative artificial intelligence…”).                                                 | Sustituye cada mención de IA por tu nuevo dominio.                  |
| `backend/agent/llms/pedagogical_response_generator.py`    | **`system_prompt_text`** - Primera línea (idéntica a la anterior).                                                                                                                                                                                          | Igual que arriba: adaptar la descripción al nuevo campo temático.                                                     |
| `backend/agent/llms/deny_response_generator.py`           | **`system_prompt_text` completo** | Reemplaza **todas** las menciones a “artificial intelligence”, “AI”, “education” y derivados por tu nuevo dominio (p. ej. “cocina”, “gastronomía”). Mantén la estructura de cortesía y la lógica de negar preguntas fuera de tema. |
| `backend/agent/llms/no_retrieval_response_generator.py`   | **`system_prompt_text` completo** | Igualmente, busca y reemplaza todas las referencias temáticas (incluido el nombre del bot “Aprende IA”) por el nuevo dominio. Asegúrate de que la parte que describe al chatbot y sus fuentes quede coherente.                     |

Con esto el backend quedará especializado al nuevo dominio y seguirá rechazando cualquier pregunta que no se relacione con él. _Cabe destacar que seguramente también resulte necesario actualizar el corpus, como se indicó anteriormente, ya que las consultas de información tienen que ser basadas en las fuentes curadas, y el corpus actual está centrado en el dominio restringido original_.
