import os

from dotenv import load_dotenv
from ai_engineer_tienda_hogar.config import Config
# from ai_engineer_tienda_hogar.agent.embeddings.indexer import Indexer
from ai_engineer_tienda_hogar.logging_config import configure_logging, get_logger
# from ai_engineer_tienda_hogar.agent.tools.order_estatus.order_status import consultar_estado_pedido
from ai_engineer_tienda_hogar.agent.graphs.graph import GraphBuilder
from langchain_core.messages import HumanMessage

load_dotenv("../.env", override=True)

# Load env vars
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_API_ENDPOINT")
os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_API_KEY")
os.environ["OPENAI_API_VERSION"] = os.getenv("OPENAI_API_VERSION")

configure_logging()
logger = get_logger(__name__)

if __name__ == "__main__":
    logger.info("Application started")
    config = Config()
    
    # Create or update vectordb
    # indexer.update_or_create_indexer()
    
    # Load vectordb
    # vectordb = indexer.get_indexer() 

    # logger.info(consultar_estado_pedido("ORD-1001"))     
    # logger.info(consultar_estado_pedido("ORD-9000")) 
    # 
    graph_builder = GraphBuilder(config.get_llm_model(), 
                         config.get_text_embedding_model(),
                         'ai_engineer_tienda_hogar/agent/embeddings/embeddings_db'
                         )

    graph = graph_builder.build_graph()

    msg = input("Enter your request: \n")
    res = graph.invoke({"messages": [HumanMessage(content=msg)]})

    logger.info("=="*50)
    logger.info(f"{res['messages'][-1].content}")



