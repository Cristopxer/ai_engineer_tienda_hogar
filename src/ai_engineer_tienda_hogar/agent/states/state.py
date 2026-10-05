from typing import Annotated, Literal, List
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[List, add_messages]
    retrieved_context: str
    route: Literal["contact_channel", "normal_flow"]
    contact_channel: str
    routing_reason: str