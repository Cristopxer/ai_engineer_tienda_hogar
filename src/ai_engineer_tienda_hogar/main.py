import os

from dotenv import load_dotenv
from ai_engineer_tienda_hogar.agent.embeddings.indexer import Indexer
from ai_engineer_tienda_hogar.config import Config
from ai_engineer_tienda_hogar.logging_config import configure_logging, get_logger

load_dotenv("../.env", override=True)

# Load env vars
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_API_ENDPOINT")
os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_API_KEY")

configure_logging()
logger = get_logger(__name__)

if __name__ == "__main__":
    logger.info("Application started")
    config = Config()
    indexer = Indexer(config.get_text_embedding_model(), '../../documents', 'ai_engineer_tienda_hogar/agent/embeddings/embeddings_db')
    # Create or update vectordb
    indexer.update_or_create_indexer()
    
    # Load vectordb
    vectordb = indexer.get_indexer()    

