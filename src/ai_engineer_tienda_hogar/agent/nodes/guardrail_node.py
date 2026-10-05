from typing import Literal, Optional

from pydantic import BaseModel, Field
from langchain_core.messages import AIMessage

from ai_engineer_tienda_hogar.agent.prompts.guardrail_prompt import guardrail_prompt
from ai_engineer_tienda_hogar.agent.states.state import State


class RouteDecision(BaseModel):
    route: Literal["contact_channel", "normal_flow"]
    contact_channel: Optional[str] = None
    reason: str = Field(default="")


class PolicyRouterNode:
    def __init__(self, model, contact_tool, contact_file_path: str):
        self.llm = model
        self.contact_tool = contact_tool
        self.contact_file_path = contact_file_path
        self.structured_llm = self.llm.with_structured_output(RouteDecision)

    def _pick_contact(self, contacts: dict) -> str | None:
        return (
            contacts.get("email")
            or contacts.get("whatsapp")
            or contacts.get("telegram")
            or contacts.get("phone")
        )

    def route(self, state: State):
        messages = guardrail_prompt.format_messages(
            messages=state["messages"],
            retrieved_context=state.get("retrieved_context", ""),
        )

        decision = self.structured_llm.invoke(messages)

        if decision.route == "contact_channel":
            contacts = self.contact_tool.invoke({"file_path": self.contact_file_path})
            contact_channel = self._pick_contact(contacts) or decision.contact_channel

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