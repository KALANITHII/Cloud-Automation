from typing import Literal

from langchain_core.messages import HumanMessage, AIMessage


def execution_agent_router(messages) -> Literal["add_execute_tool_message", "execute", "__end__"]:
    if isinstance(messages[-1], AIMessage) and messages[-1].tool_calls:
        return "add_execute_tool_message"
    elif not isinstance(messages[-1], HumanMessage):
        return "end"
    return "execute"
