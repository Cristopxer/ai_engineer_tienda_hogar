from ai_engineer_tienda_hogar.agent.states.state import State


class CustomerServiceNode:
    """Chatbot logic implementation"""

    def __init__(self, model):
        self.llm = model

    def create_chatbot(self, tools):
        """Returns a chatbot node function"""
        llm_tools = self.llm.bind_tools(tools)

        def chatbot_node(state: State):
            return {"messages": [llm_tools.invoke(state["messages"])]}

        return chatbot_node