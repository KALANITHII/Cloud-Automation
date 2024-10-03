import os
import subprocess

from dotenv import load_dotenv
from langchain_core.tools import tool
from schemas.cli_command_schema import AWSCLICommand

load_dotenv()


@tool("execute_aws_command", args_schema=AWSCLICommand)
def execute_aws_command(aws_cli_command: str):
    """
    Executes the provided AWS CLI command using the profile specified in the environment variable 'CURRENT_PROFILE'.

    :param aws_cli_command: The AWS CLI command to be executed as a string.
    :return: A str containing the status of the command execution and the output or error message.
    """
    my_process = subprocess.Popen(
        aws_cli_command + f" --profile {os.environ.get('CURRENT_PROFILE')}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = my_process.communicate()
    stdout = stdout.decode("utf-8") if stdout else ""
    stderr = stderr.decode("utf-8") if stderr else ""
    # print("=======================", stdout, stderr)
    if my_process.returncode != 0:
        return f"status: error,\nmessage: {stderr}"
    return f"status: success,\nmessage: {stdout}"
