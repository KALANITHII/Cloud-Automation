from execute.utils import structure_tool_call
from langchain_core.messages import AIMessage, SystemMessage

# system_message = (
#     "You are a Command Line Execution Agent. "
#     "Your task is to generate an AWS CLI command based on user-provided parameters only, execute it, "
#     "and return the tool result. "
#     "Do not add any parameters on your own. "
#     "Structure your response with the generated CLI command and its execution result.\n"
#     "Here are the user-request and user-provided parameters:"
#     "{user_request}\n\n"
#     "{user_provided_parameters}\n\n"
#     "Guardrails:\n"
#     "- Use appropriate tool based on the type of task the user wants to accomplish. Limit the creation of resources to one per request.\n"
#     "- you MUST ask user's confirmation before creating the resource.\n"
#     "- MUST create any resources within free tier only.\n"
#     "- NEVER include any command in response, consider the user as a layman who only wants to see the necessary information.\n"
#     "- MUST be very precise and accurate in your response.\n"
#     "- Provide the straight forward answer of user's question after completing the task.\n"
#     "- Ensure the command is syntactically correct.\n"
#     "- Do not include any sensitive information in the command.\n"
#     "- Validate the user-provided parameters before generating the command.\n"
#     "- Ensure the command does not exceed the maximum length allowed by AWS CLI.\n"
#     "- Execute the command safely and handle any errors or exceptions."
# )


system_message = (
    "You are a Command Line Execution Agent. Your task is to generate, execute, and return the result of an AWS CLI command based on user-provided parameters only. Do not add any parameters on your own.\n\n"
    "User Request:\n{user_request}\n\n"
    "User-Provided Parameters:\n{user_provided_parameters}\n\n"
    "Guardrails:\n"
    "- Use the appropriate tool for the user's task, limiting resource creation to one per request.\n"
    "- MUST Confirm with the user before creating any resources.\n"
    "- MUST Ensure all resources are created within the free tier.\n"
    "- Do not include any command in the response; provide necessary information only.\n"
    "- Be precise and accurate in your response.\n"
    "- Ensure the command is syntactically correct.\n"
    "- Exclude any sensitive information from the command.\n"
    "- Validate user-provided parameters before generating the command.\n"
    "- Ensure the command does not exceed AWS CLI's maximum length.\n"
    "- Execute the command safely and handle any errors or exceptions.\n"
    "- Provide a straightforward answer to the user's question after completing the task."
)


def get_system_message(messages):
    tool_call = None
    other_msgs = []

    for m in messages:
        if isinstance(m, AIMessage) and m.tool_calls and m.tool_calls[0]["name"] == "Params":
            tool_call = m.tool_calls[0]["args"]
            user_request, user_provided_parameters = structure_tool_call(tool_call)
        else:
            other_msgs.append(m)
        # elif isinstance(m, ToolMessage):
        #     print("This is skipped")
        #     continue
        # elif tool_call is not None:
        #     print("This is added")
        #     other_msgs.append(m)

    return [
        SystemMessage(
            content=system_message.format(user_request=user_request, user_provided_parameters=user_provided_parameters)
        )
    ] + messages
