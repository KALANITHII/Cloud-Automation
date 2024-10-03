from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage


def planner_agent_router(messages) -> Literal["add_param_tool_message", "agent", "__end__"]:
    if messages[-1].tool_calls == "aws_cli_get_tool":
        return "aws_cli_get_tool"
    elif isinstance(messages[-1], AIMessage) and messages[-1].tool_calls:
        return "add_param_tool_message"
    elif not isinstance(messages[-1], HumanMessage):
        return "end"
    return "agent"
