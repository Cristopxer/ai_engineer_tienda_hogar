from langchain_core.tools.retriever import create_retriever_tool
from ai_engineer_tienda_hogar.agent.embeddings.indexer import Indexer

class Retriever():
    def __init__(self, emb_model:str, db_path:str):
        self.indexer = Indexer(model_name=emb_model, db_path=db_path)                

    def get_retriever(self, k:int):
        """Configure vector db retriever as langchain retriever tool
        Args:
            k:int = number of top matches"""    
        # Load vectordb
        vectordb = self.indexer.get_indexer(k)                
        return create_retriever_tool(
            vectordb,
            'knowledgebase_tiendahogar',
            'Information about company policies, contact channels, refunds'
        )