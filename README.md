# ProyGrad2024

**Crear un entorno virtual (parados en el directorio del repositorio):**

python3 -m venv proygrad_venv

**Activar el entorno virtual:**

source proygrad_venv/bin/activate

*Este comando ejecuta el script activate que se encuentra en el directorio bin dentro del entorno virtual. El script configura el entorno de shell actual para usar los paquetes y la configuración del entorno virtual. Realiza varios cambios como modificar la variable de entorno PATH, modificar el prompt del shell (la parte que se muestra antes de que escribas un comando) para indicar que estás en un entorno virtual, entre otras cosas.*

*Para desactivar el entorno virtual correr: deactivate*

**Instalar los paquetes Python requeridos para el proyecto:**

pip3 install -r requirements.txt

**Correr el prototipo:**

cd prototipo

streamlit run streamlit_app_rag.py