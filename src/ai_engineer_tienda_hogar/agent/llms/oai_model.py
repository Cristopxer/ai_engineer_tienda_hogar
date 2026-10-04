from langchain_openai import AzureChatOpenAI
from ai_engineer_tienda_hogar.logging_config import get_logger

logger = get_logger(__name__)

class OAIChatModel():
    def __init__(self, model_name: str, temperature: float = 0.0):
        """
        Args:
            model_name (str): The Azure OpenAI deployment name.
            temperature (float): Controls randomness.
        """
        self.model_name = model_name
        self.temperature = temperature

    def get_model(self) -> AzureChatOpenAI:
        """Setup Azure OpenAI Chat Model connection"""
        logger.info(f"Setting up Azure OpenAI Chat model connection for deployment: {self.model_name}")
        
        chat_model = AzureChatOpenAI(
            azure_deployment=self.model_name,
            temperature=self.temperature
        )

        return chat_model