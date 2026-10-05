from ai_engineer_tienda_hogar.agent.states.state import State

class RetrievalContextNode:
    def __init__(self, retriever_tool):
        self.retriever_tool = retriever_tool        

    def retrieve(self, state: State):

        user_message = state["messages"][-1].content
        retrieved = self.retriever_tool.invoke(f"{user_message}")

        return {
            "retrieved_context": str(retrieved),
        }