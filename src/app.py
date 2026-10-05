import os
import uvicorn
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from langchain_core.messages import HumanMessage
from ai_engineer_tienda_hogar.config import Config
from ai_engineer_tienda_hogar.logging_config import configure_logging, get_logger
from ai_engineer_tienda_hogar.agent.graphs.graph import GraphBuilder
from ai_engineer_tienda_hogar.agent.embeddings.indexer import Indexer

load_dotenv(".env", override=True)

# Load env vars
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_API_ENDPOINT")
os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_API_KEY")
os.environ["OPENAI_API_VERSION"] = os.getenv("OPENAI_API_VERSION")

configure_logging(Path(__file__).resolve().parent / "logs")
logger = get_logger(__name__)

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("Incoming request: %s %s", request.method, request.url.path)
    response = await call_next(request)
    logger.info("Completed request: %s %s -> %s", request.method, request.url.path, response.status_code)
    return response

@app.post("/chat")
async def chat(request:Request):
    config = Config("src/ai_engineer_tienda_hogar/config.ini")
    data = await request.json()
    message = data.get("message", "")
    if message:
        graph_builder = GraphBuilder(config.get_llm_model(), 
                            config.get_text_embedding_model(),
                            'src/ai_engineer_tienda_hogar/agent/embeddings/embeddings_db',
                            'src/ai_engineer_tienda_hogar/documents/canales_contacto.md'
                            )

        graph = graph_builder.build_graph()
        res = graph.invoke({"messages": [HumanMessage(content=message)]})
    else:
        return {'error': 'message is required'}

    return {'data': res['messages'][-1].content}

@app.post("/index/update")
async def update_embedding_index():
    logger.info("Updating index")
    config = Config("src/ai_engineer_tienda_hogar/config.ini")
    indexer = Indexer(
        config.get_text_embedding_model(),
        "src/ai_engineer_tienda_hogar/agent/embeddings/embeddings_db",
    )
    indexer.update_or_create_indexer()
    
    return {"status": "index updated successfully"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True, log_config=None)

