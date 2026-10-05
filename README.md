# ai_engineer_tienda_hogar

Agente de soporte al cliente para Tienda Hogar, implementado con **Python**, **LangGraph**, **RAG**, **FastAPI** y **Azure OpenAI**. El sistema responde preguntas de clientes usando una base de conocimiento documental, consulta el estado de pedidos desde una tabla local y aplica un guardrail para derivar casos sensibles al canal humano cuando los documentos así lo indican.

## Características

- Respuestas basadas en documentos de conocimiento (RAG)
- Consulta de estado de pedidos con tool dedicada
- Guardrail para redirigir casos que requieren atención humana
- API HTTP con FastAPI
- Logging personalizado
- Evaluación automatizada con pytest y casos semánticos con Langsmith (LLM as judge)

## Requisitos

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) como gestor de paquetes
- Acceso a Microsoft Foundry KEY and ENDPOINT
- Langsmith/Langchain API KEY para ejecutar los test (llm_as_judge
- Variables de entorno configuradas en `.env`

Ejemplo de variables esperadas usa `.env.example como referencia`:

```env
AZURE_API_ENDPOINT = ...
AZURE_API_KEY =  ...
OPENAI_API_VERSION = ...
LANGSMITH_API_KEY  = ...
```

## Instalación con uv

Desde la raíz del proyecto:

```powershell
uv sync
```

Si necesitas crear el entorno e instalar dependencias desde cero:

```powershell
uv venv
uv sync
```

## Ejecutar el agente localmente

El agente se puede ejecutar directamente desde la carpeta raiz.

### activando el entorno

```powershell
.venv\Scripts\activate
```

## Ejecutar la API FastAPI

El archivo `src/app.py` expone un endpoint POST `/chat`.

### Con uvicorn en la raiz

```powershell
uvicorn src.app:app
```
## Docker

El proyecto incluye archivos Docker en la raíz:

Construye la imagen y levanta el servicio (asegurate de tener tus variables en `.env`):

```powershell
docker compose up --build
```

## Consumir la API con curl

Una vez corriendo la app:

```powershell
curl -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d '{"message": "Que necesito para poder devolver un producto?"}'
```

Respuesta esperada:

```json
{
  "data": "Para poder devolver un producto en Tienda Hogar, debe cumplir ..."
}
```

## Correr los tests

Los tests principales están en `tests/pytests/`.

```powershell
pytest tests\pytests\test_cases.py
```

### Test de evaluación con LLM as judge

También hay pruebas/evaluación orientadas a la comparación semántica del agente.

```powershell
python tests\llm_as_judge\test_cases.py
```

## Estructura del proyecto

```text
ai_engineer_tienda_hogar/
├─ Dockerfile                      # Imagen base para ejecutar la API con uvicorn
├─ docker-compose.yml              # Orquestación local del servicio app
├─ pyproject.toml                  # Dependencias y configuración del proyecto
├─ uv.lock                         # Lockfile de dependencias (si aplica)
├─ src/
│  ├─ app.py                       # API FastAPI
│  └─ ai_engineer_tienda_hogar/
│     ├─ config.py                 # Configuración del proyecto
│     ├─ logging_config.py         # Logging personalizado
│     ├─ agent/
│     │  ├─ graphs/                # Grafo principal de LangGraph
│     │  ├─ nodes/                 # Nodos del flujo (chat, guardrail, retrieval)
│     │  ├─ prompts/               # Prompts del sistema
│     │  ├─ tools/                 # Tools del agente
│     │  ├─ embeddings/           # Indexador y base vectorial local
│     │  └─ states/                # Estado del grafo
│     └─ documents/                # Base de conocimiento en Markdown
├─ tests/
│  ├─ pytests/                     # Tests de validación del agente
|  |  └─ results/                    # Resultados generados por las pruebas
│  └─ llm_as_judge/                # Evaluaciones con LLM as judge / LangSmith
|     └─ results/                    # Resultados generados por las pruebas
│  
└─ README.md
```

## Cómo funciona la solución

1. El usuario envía una solicitud al agente.
2. El grafo recupera contexto relevante desde los documentos.
3. El guardrail decide si la consulta debe seguir el flujo normal o derivarse a un canal humano.
4. Si la solicitud es normal, el chatbot responde usando RAG y tools.
5. Si la solicitud requiere soporte humano, el sistema redirige al canal oficial.

## Documentación y conocimiento

La base de conocimiento del agente está en `src/ai_engineer_tienda_hogar/documents/`.

## Notas

- El proyecto usa embeddings locales y FAISS para el prototipo.
- El guardrail se basa en el contenido recuperado desde la base documental.
- Los tests validan tanto la respuesta factual como el comportamiento de routing.
