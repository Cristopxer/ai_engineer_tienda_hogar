import os
from pathlib import Path

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from ai_engineer_tienda_hogar.logging_config import get_logger
from ai_engineer_tienda_hogar.agent.llms.oai_embedding import OAIEmbeddings

logger = get_logger(__name__)

class Indexer():
    def __init__(self, model_name:str, db_path:str, docs_path:str = "../../documents"):
        """Vector db functionalities
        
        Args:
            model_name (str) = Azure Open AI Embbedings model deployment name.
            docs_path (str) = Documents path.
            db_path (str) = Path where to save/load the vector db.
        """
        self.emb_model_name = model_name
        self.docs_path = docs_path
        self.db_path = db_path
        self.oai_emb = OAIEmbeddings(self.emb_model_name).get_model()

    def load_files(self):
        """Load files to build vector db"""
        # Load documents
        documents_path = Path(__file__).resolve().parent / self.docs_path
        docs = []

        # Create folder if not exists.
        if not documents_path.exists():
            documents_path.mkdir(parents=True, exist_ok=True)
            logger.info("Created folder: %s. Please add your .md files.", documents_path)

        for filename in os.listdir(documents_path):
            if filename.endswith(".md"):
                file_path = os.path.join(documents_path, filename)
                
                # Open and read the markdown file
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read().strip()
                                        
                    if content:                        
                        doc = Document(
                            page_content=content,
                            metadata={"source": filename}
                        )
                        docs.append(doc)
                        logger.info(f"Loaded: {filename}")

        if not docs:
            raise ValueError("No valid .md files found in the documents folder.")

        return docs


    def update_or_create_indexer(self):
        """Build vector db"""
        logger.info("Loading documents ...")
        docs = self.load_files()
        logger.info(docs)

        logger.info(f"Generating embeddings with model {self.emb_model_name}")        
        vectordb = FAISS.from_documents(docs, self.oai_emb)
        
        vectordb.save_local(self.db_path)
        logger.info(f"Embeddings db succesfully saved: {self.db_path}")

    def get_indexer(self, k:int = 2):
        """Load vector db from local
        Args:
            k (int) = number of top matches
        """        
        vectordb = FAISS.load_local(
            self.db_path,
            self.oai_emb,
            allow_dangerous_deserialization=True
        )

        return vectordb.as_retriever(search_kwargs={"k": k})




        



        

