# Load libraries
from dotenv import load_dotenv
from google import genai
import json
import os


# Load environment variables from .env file
load_dotenv()


# Initialize the GenAI client with the API key from environment variables
client = None
try:
    api_key = os.getenv("GENAI_API_KEY")
    client = genai.Client(api_key=api_key)
    print("Se ha inicializado el cliente de GenAI correctamente.")
except Exception as e:
    print(f"Error al inicializar el cliente de GenAI: {e}")
    exit(1)


# Function to generate a brief introduction
def presentarse():
    response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents="En forma breve quiero que te presentes y menciones ¿qué puedes hacer por nosotros?"
    )

    print(response.text)


# Function to read and concatenate code files from a directory
def obtener_codigo(directorio_api):
    """Recorre el directorio y concatena el contenido de los archivos relevantes."""
    codigo_completo = ""
    # Define qué archivos de la API quieres revisar
    extensiones = ('.js', '.ts', '.mjs')

    for ruta_raiz, _, archivos in os.walk(directorio_api):
        for nombre_archivo in archivos:
            if nombre_archivo.endswith(extensiones) and 'node_modules' not in ruta_raiz:
                ruta_completa = os.path.join(ruta_raiz, nombre_archivo)
                with open(ruta_completa, 'r', encoding='utf-8') as f:
                    codigo_completo += f"\n\n--- INICIO ARCHIVO: {nombre_archivo} ---\n"
                    codigo_completo += f.read()
                    codigo_completo += f"\n--- FIN ARCHIVO: {nombre_archivo} ---\n"
    return codigo_completo


def analizar_con_ia(codigo):
    """Envía el código a la IA con un prompt detallado."""

    # El prompt es la parte MÁS IMPORTANTE
    my_prompt = f"""
    Eres un auditor de seguridad de código experto en Express.js y MongoDB (Mongoose).
    Analiza el siguiente código fuente de un API y realiza una revisión exhaustiva.

    Tu análisis debe enfocarse en:
    1.  **Seguridad NoSQL:** Identificar cualquier vulnerabilidad de **Inyección NoSQL**, especialmente en consultas de MongoDB que usan directamente la entrada del usuario (`req.body`, `req.query`, `req.params`) sin sanitización.
    2.  **Manejo de Errores:** Verificar el uso correcto de `async/await` y la gestión de errores en los bloques `try...catch` en los controladores (middleware).
    3.  **Configuración de Respuestas:** Detectar si las respuestas exponen datos sensibles (contraseñas, hashes, claves) o si se están usando códigos de estado HTTP incorrectos (ej. 200 en lugar de 400).
    4.  **Rendimiento:** Comentar sobre la eficiencia de las consultas de Mongoose (ej. falta de indexación o uso de `.lean()`).

    Devuelve el resultado en un formato de lista de problemas clara (Markdown o JSON).

    CÓDIGO A ANALIZAR:\n
    {codigo}
    """

    try:
        # Llama a tu modelo de IA
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=my_prompt
        )
        return response.text
    except Exception as e:
        return f"Error al contactar a la IA: {e}"


def crea_test(codigo):
    my_prompt = f"""
    Actúa como un desarrollador de Node.js experto en Jest. 
    Genera pruebas unitarias para la siguiente función de Express.js. 
    ES CRÍTICO que utilices Jest para mockear (simular) todas las llamadas a Mongoose/MongoDB para aislar la lógica de la función. 
    Incluye pruebas para la 'ruta feliz' y un caso de error 404. 
    
    CÓDIGO A TESTEAR:\n
    {codigo} 
    """

    try:
        # Llama a tu modelo de IA
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=my_prompt
        )
        return response.text
    except Exception as e:
        return f"Error al contactar a la IA: {e}"


# Call the function to presentarse
presentarse()

# Directory containing the API code
directorio_api = 'D:/Documentos/Cursos UTN/2025 - 2/ITI-523 - Tecnologías y Sistemas Web II/Apis/class_04d'
# Get the complete code from the specified directory
#codigo_api = obtener_codigo(directorio_api)
#print("Se ha obtenido el código de la API.")
#print(codigo_api)

# Analyze the code with AI
#resultado_analisis = analizar_con_ia(codigo_api)
#print("Resultado del análisis de IA:")
#print(resultado_analisis)

# Generate tests for a specific function (example function code)
funcion_ejemplo = directorio_api + '/controllers/ctrl_Users.js'
codigo_funcion = obtener_codigo(funcion_ejemplo)
resultado_tests = crea_test(codigo_funcion)
print("Resultado de la generación de tests:")
print(resultado_tests)
