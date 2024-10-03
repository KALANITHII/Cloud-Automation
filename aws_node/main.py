import datetime
import uuid

from draw_graph import draw_graph
from execute import execution_agent_router, execution_agent_runnable
from general_conversation import general_conversation_agent_runnable
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, MessageGraph
from plan import planner_agent_router, planner_agent_runnable
from supervisor import supervisor_agent_router, supervisor_agent_runnable
from tools import aws_cli_get_tool, execute_aws_command

# from tools.aws_cli_get_tool import AWSCLIGetTool

workflow = MessageGraph()

# Construct Graph
# llm = ChatOpenAI(model="gpt-3.5-turbo", api_key="")

workflow.add_node("supervisor", supervisor_agent_runnable)
workflow.add_node("agent", planner_agent_runnable)
workflow.add_node("execute", execution_agent_runnable)
workflow.add_node("general_conversation", general_conversation_agent_runnable)


@workflow.add_node
def add_param_tool_message(messages):
    return ToolMessage(content="parameters collected", tool_call_id=messages[-1].tool_calls[0]["id"])


# @workflow.add_node
# def function_aws_cli_get_tool(messages):
#     return ToolMessage(
#         content=aws_cli_get_tool.invoke(messages[-1].tool_calls[0]["args"]),
#         tool_call_id=messages[-1].tool_calls[0]["id"],
#     )


# workflow.add_node("aws_cli_get_tool", AWSCLIGetTool)


@workflow.add_node
def add_execute_tool_message(messages):
    return ToolMessage(
        content=execute_aws_command.invoke(messages[-1].tool_calls[0]["args"]),
        tool_call_id=messages[-1].tool_calls[0]["id"],
    )


# workflow.add_edge("function_aws_cli_get_tool", "agent")
workflow.add_edge("add_param_tool_message", "execute")

workflow.set_entry_point("supervisor")

workflow.add_conditional_edges(
    "supervisor",
    supervisor_agent_router,
    {"agent": "agent", "general_conversation": "general_conversation"},
)

workflow.add_edge("general_conversation", END)

workflow.add_conditional_edges(
    "agent",
    planner_agent_router,
    {
        "add_param_tool_message": "add_param_tool_message",
        "agent": "agent",
        "end": END,
        # "aws_cli_get_tool": "function_aws_cli_get_tool",
    },
)

workflow.add_conditional_edges(
    "execute",
    execution_agent_router,
    {"add_execute_tool_message": "add_execute_tool_message", "execute": "execute", "end": END},
)

workflow.add_edge("add_execute_tool_message", "execute")
# memory = SqliteSaver.from_conn_string("checkpoint.sqlite")


# config = {"configurable": {"thread_id": uuid.uuid4(), "thread_ts": datetime.datetime.utcnow()}}

# graph = workflow.compile(checkpointer=memory)
graph = workflow.compile()
# draw_graph(graph)
# print(graph.invoke("create me s3 bucket", config=config, debug=True))

# memory.put(config=config, checkpoint=[])
# messages = []
#
# while True:
#     user_message = input("User (q/Q to quit): ")
#     if user_message in {"q", "Q"}:
#         print("Bye!")
#         break
#
#     messages.append({"role": "user", "content": user_message})
#
#     output = graph.invoke(messages[-7:])
#     # output = graph.invoke(messages)
#
#     # print(f"\n\n{'='*50}\n\n")
#     # print(
#     #     "\n\n".join(
#     #         [
#     #             f"model: {message.response_metadata['model_name'] if message.response_metadata else '-'}"
#     #             f" | content: {message.content}"
#     #             for message in output
#     #         ]
#     #     )
#     # )
#     # print(f"\n\n{'='*50}\n\n")
#
#     ai_message = output[-1].content
#
#     messages.append({"role": "assistant", "content": ai_message})
#
#     print(ai_message)
#
#     # for output in graph.stream(user_message, history, config=config, stream_mode="updates", debug=True):
#     #     last_message = next(iter(output.values()))
#     #     last_message.pretty_print()
