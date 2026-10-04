import re
from typing import Literal, Optional

from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field

from ai_engineer_tienda_hogar.agent.states.state import State


class RouteDecision(BaseModel):
    route: Literal["contact_channel", "normal_flow"]
    contact_channel: Optional[str] = None
    reason: str = Field(default="")


class PolicyRouterNode:
    def __init__(self, model):
        self.llm = model
        self.structured_llm = self.llm.with_structured_output(RouteDecision)

    def route(self, state: State):
        user_message = state["messages"][-1].content
        retrieved_context = state.get("retrieved_context", "")

        prompt = f"""
You are a guardrail router for Tienda Hogar.

Use ONLY the retrieved context.
Decide whether the user's request matches a scenario that should be handled through the official contact channel.

Rules:
- Do not invent policies.
- Do not invent contact channels.
- If the request matches a protected scenario in the retrieved context, route to "contact_channel".
- If not, route to "normal_flow".
- If the contact channel is present in the retrieved context, extract it exactly.

User message:
{user_message}

Retrieved context:
{retrieved_context}
"""

        decision = self.structured_llm.invoke(prompt)

        if decision.route == "contact_channel":            
            contact_channel = decision.contact_channel

            message = (
                f"Para este caso, por favor contacta el canal oficial de soporte: {contact_channel}."
                if contact_channel
                else "Para este caso, por favor contacta el canal oficial de soporte."
            )

            return {
                "route": "contact_channel",
                "contact_channel": contact_channel or "",
                "messages": [AIMessage(content=message)],
            }

        return {
            "route": "normal_flow",
            "contact_channel": "",
        }