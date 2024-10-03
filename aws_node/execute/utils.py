def structure_tool_call(tool_call):
    user_request = f"user_request {tool_call['user_request']}"

    required_params = tool_call["required_params"]
    optional_params = tool_call["optional_params"]

    user_provided_parameters = "user provided parameters with key and value: \n"
    for param in required_params:
        user_provided_parameters += f"key: {param['key']}, value: {param['value']}\n"
    for param in optional_params:
        if param["value"] is not None:
            user_provided_parameters += f"key: {param['key']}, value: {param['value']}\n"

    return user_request, user_provided_parameters
