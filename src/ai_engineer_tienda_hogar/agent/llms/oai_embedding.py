from langchain_openai import AzureOpenAIEmbeddings

from ai_engineer_tienda_hogar.logging_config import get_logger

logger = get_logger(__name__)

class OAIEmbeddings():
    def __init__(self, model_name:str):
        self.model = model_name

    def get_model(self):
        """Setup embeddings model conection"""
        # Embedding model
        logger.info("Seting up embeddings model")
        embeddings = AzureOpenAIEmbeddings(
            model= self.model
        )

        return embeddings