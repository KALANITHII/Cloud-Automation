from typing import Literal


def supervisor_agent_router(messages) -> Literal["agent", "general_conversation"]:
    if messages[-1].content.lower() == "true":
        return "agent"
    return "general_conversation"
