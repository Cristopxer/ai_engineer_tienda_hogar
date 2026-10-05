from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from ai_engineer_tienda_hogar.agent.states.state import State
from ai_engineer_tienda_hogar.agent.llms.oai_model import OAIChatModel
from ai_engineer_tienda_hogar.agent.tools.retriever.retriever import Retriever
from ai_engineer_tienda_hogar.agent.nodes.guardrail_node import PolicyRouterNode
from ai_engineer_tienda_hogar.agent.nodes.retrieval_node import RetrievalContextNode
from ai_engineer_tienda_hogar.agent.nodes.customer_service_node import CustomerServiceNode
from ai_engineer_tienda_hogar.agent.tools.order_estatus.order_status import consultar_estado_pedido
from ai_engineer_tienda_hogar.agent.tools.contact_channels.contact_channels import extract_contact_channels

class GraphBuilder:
    def __init__(self, model_name: str, emb_model_name: str, db_path: str, contact_file_path:str):
        self.model_name = model_name
        self.emb_model_name = emb_model_name
        self.db_path = db_path
        self.contact_file_path = contact_file_path
        self.graph_builder = StateGraph(State)

    def build_graph(self):
        retriever_tool = Retriever(self.emb_model_name, self.db_path).get_retriever(1)
        order_status_tool = consultar_estado_pedido
        tools = [retriever_tool, order_status_tool]
        tools_node = ToolNode(tools)

        model = OAIChatModel(self.model_name, 0).get_model()
        csr_model = OAIChatModel(self.model_name, 0.3).get_model()

        chat_node = CustomerServiceNode(csr_model).create_chatbot(tools)
        policy_router_node = PolicyRouterNode(model,
                                              extract_contact_channels,
                                              self.contact_file_path
                                              )
        retrieval_node = RetrievalContextNode(retriever_tool)

        self.graph_builder.add_node("retrieve_context", retrieval_node.retrieve)
        self.graph_builder.add_node("policy_router", policy_router_node.route)
        self.graph_builder.add_node("chat", chat_node)
        self.graph_builder.add_node("tools", tools_node)

        self.graph_builder.add_edge(START, "retrieve_context")
        self.graph_builder.add_edge("retrieve_context", "policy_router")

        self.graph_builder.add_conditional_edges(
            "policy_router",
            lambda state: state["route"],
            {
                "contact_channel": END,
                "normal_flow": "chat",
            },
        )

        self.graph_builder.add_conditional_edges("chat", tools_condition)
        self.graph_builder.add_edge("tools", "chat")

        return self.graph_builder.compile()