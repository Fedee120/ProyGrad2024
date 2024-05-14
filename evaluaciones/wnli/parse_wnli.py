import pandas as pd

# Cargar el archivo CSV
df = pd.read_csv('wnli-dev-es.csv')

# Crear el 'prompt' combinando 'sentence1' y 'sentence2' y especificando claramente la pregunta
df['prompt'] = df.apply(lambda x: f"Basado en la oración: '{x['sentence1']}' ¿Es correcto decir que: '{x['sentence2']}'? Responde 'true' si es correcto y 'false' si no.", axis=1)

# Crear 'referenceResponse' basado en la columna 'label'
df['referenceResponse'] = df['label'].apply(lambda x: 'true' if x == 1 else 'false')

# Seleccionar solo las columnas necesarias
df = df[['prompt', 'referenceResponse']]

# Convertir el dataframe a formato JSON Lines y guardar con la extensión correcta
df.to_json('wnli-dev-es.jsonl', orient='records', lines=True, force_ascii=False)

print("El archivo JSON Lines ha sido creado exitosamente.")
