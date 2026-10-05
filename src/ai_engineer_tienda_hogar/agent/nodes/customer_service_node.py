from ai_engineer_tienda_hogar.agent.prompts.customer_service_prompt import customer_service_prompt
from ai_engineer_tienda_hogar.agent.states.state import State


class CustomerServiceNode:
    """Chatbot logic implementation"""

    def __init__(self, model):
        self.llm = model

    def create_chatbot(self, tools):
        """Returns a chatbot node function"""
        llm_tools = self.llm.bind_tools(tools)

        def chatbot_node(state: State):
            retrieved_context = state.get("retrieved_context", "")

            messages = customer_service_prompt.format_messages(
                messages=state["messages"],
                retrieved_context=retrieved_context,
            )

            return {"messages": [llm_tools.invoke(messages)]}

        return chatbot_node