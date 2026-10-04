from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from ai_engineer_tienda_hogar.agent.llms.oai_model import OAIChatModel
from ai_engineer_tienda_hogar.agent.nodes.customer_service_node import CustomerServiceNode
from ai_engineer_tienda_hogar.agent.states.state import State
from ai_engineer_tienda_hogar.agent.tools.order_estatus.order_status import consultar_estado_pedido
from ai_engineer_tienda_hogar.agent.tools.retriever.retriever import Retriever


class GraphBuilder:
    def __init__(self, model_name: str, emb_model_name: str, db_path: str):
        self.model_name = model_name
        self.emb_model_name = emb_model_name
        self.db_path = db_path
        self.graph_builder = StateGraph(State)

    def build_graph(self):
        """Builds tienda hogar customer service graph"""

        # tools
        retriever_tool = Retriever(self.emb_model_name, self.db_path).get_retriever()
        order_status_tool = consultar_estado_pedido
        tools = [retriever_tool, order_status_tool]
        tools_node = ToolNode(tools)

        # llm
        model = OAIChatModel(self.model_name, 0).get_model()

        # Nodes
        chat_node = CustomerServiceNode(model)
        chat_node = chat_node.create_chatbot(tools)
        tools_node = ToolNode(tools)

        self.graph_builder.add_node("chat", chat_node)
        self.graph_builder.add_node("tools", tools_node)

        # Edges
        self.graph_builder.add_edge(START, "chat")
        self.graph_builder.add_conditional_edges("chat", tools_condition)
        self.graph_builder.add_edge("tools", "chat")

        return self.graph_builder.compile()





    
        
    