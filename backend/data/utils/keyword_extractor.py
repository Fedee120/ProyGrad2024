from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Keywords(BaseModel):
    """Estructura para las keywords extraídas del texto."""
    keywords: List[str] = Field(
        description="Lista de keywords relevantes extraídas del texto",
    )

def extract_keywords(text: str) -> List[str]:
    """
    Extrae keywords de un texto usando GPT-4o-mini con output estructurado.
    Retorna una lista de keywords relevantes (entre 1 y 10).
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    ).with_structured_output(Keywords)
    
    prompt = f"""Analiza el siguiente texto y extrae las keywords más relevantes.
    Las keywords deben ser sustantivos o frases nominales cortas que representen los conceptos principales del texto. Limitate a 5 keywords como máximo.
    
    TEXTO:
    {text}
    """
    
    try:
        result = llm.invoke(prompt)
        # Asegurarnos de que la lista no esté vacía y limitar a 5 elementos
        if not result.keywords:
            return []
        return result.keywords[:min(5, len(result.keywords))]
    except Exception as e:
        print(f"Error al extraer keywords: {e}")
        return [] 
    
if __name__ == "__main__":
    print(extract_keywords("""Las GAN se entrenan a sí mismas. El generador crea falsicaciones mientras que el
generador y los ejemplos verdaderos. Cuando el discriminador puede marcar la
falsicación, el generador es penalizado. El ciclo de retroalimentación continúa hasta
que el generador logra producir una salida que el discriminador no puede distinguir. El principal benecio de la GAN es crear resultados realistas que pueden ser difíciles
de distinguir de los originales, que, a su vez, se pueden emplear para entrenar aún
más los modelos de aprendizaje automático. Congurar una GAN para aprender es
sencillo, ya que se capacitan mediante el uso de datos sin etiquetar o con un
etiquetado menor. Sin embargo, la desventaja potencial es que el generador y el
discriminador pueden ir y venir en competencia durante mucho tiempo, creando un
gran drenaje del sistema. Una limitación del entrenamiento es que puede ser
necesaria una gran cantidad de datos de entrada para obtener un resultado
satisfactorio. Otro problema potencial es el "colapso de modo", cuando el generador
produce un conjunto limitado de salidas en lugar de una variedad más amplia. Modelos de difusión
Los modelos de difusión son modelos generativos que se entrenan mediante el
proceso de difusión directa e inversa de adición y eliminación de ruido progresivas. Los modelos de difusión generan datos (la mayoría de las veces imágenes) similares a
los datos con los que se entrenan, pero luego sobreescriben los datos empleados para
entrenarlos. Agregan gradualmente ruido gaussiano a los datos de entrenamiento
hasta que es irreconocible, luego aprenden un proceso inverso de "eliminación de
ruido" que puede sintetizar la salida (generalmente imágenes) a partir de la entrada
de ruido aleatorio. Un modelo de difusión aprende a minimizar las diferencias de las muestras generadas
frente al objetivo deseado. Cualquier discrepancia se cuantica y los parámetros del
modelo se actualizan para minimizar la pérdida, entrenando el modelo para producir
muestras que se parezcan mucho a los datos de entrenamiento auténticos.precisión. El resultado depende de la entrada y de lo bien 
entrenadas que estén las
capas en el modelo generativo para este caso de uso. El discriminador es el adversario, donde el resultado generativo (imagen falsa) se
compara con las imágenes reales en el conjunto de datos. El discriminador intenta
distinguir entre las imágenes, el video o el audio reales y falsos.–7/27/24, 10:44 PM ¿Qué es el aprendizaje profundo? | IBM      
https://www.ibm.com/mx-es/topics/deep-learning 10/21"""))
    
    print(extract_keywords("""
de aprendizaje automático “no profundos” emplean redes neuronales simples con
una o dos capas computacionales. Los modelos de aprendizaje profundo emplean tres
o más capas, pero normalmente cientos o miles de capas, para entrenar los modelos. Mientras que los modelos de aprendizaje supervisado requieren datos de entrada
estructurados y etiquetados para obtener resultados precisos, los modelos de
aprendizaje profundo pueden emplear el aprendizaje no supervisado. Con el
aprendizaje no supervisado, los modelos de aprendizaje profundo pueden extraer las
características, las funciones y las relaciones que necesitan para obtener resultados
precisos a partir de datos brutos y no estructurados. Además, estos modelos pueden
incluso evaluar y renar sus resultados para aumentar la precisión. El aprendizaje profundo es un aspecto de la ciencia de datos que impulsa muchas
aplicaciones y servicios que mejoran la automatización, realizando tareas analíticas y
físicas sin intervención humana. Esto permite muchos productos y servicios
cotidianos, como asistentes digitales, controles remotos de TV habilitados por voz,
detección de fraudes con tarjetas de crédito, vehículos autónomos e IA generativa. Contenido relacionadoLibro electrónico
Desarrolle flujos de trabajo de IA responsables con gobernanza de IA
Conozca los componentes básicos y las mejores prácticas para ayudar a sus equipos a
acelerar la IA responsable. Regístrese para obtener el libro electrónico sobre IA generativa7/27/24, 10:44 PM ¿Qué es el aprendizaje profundo? | IBM
https://www.ibm.com/mx-es/topics/deep-learning 3/21"""))