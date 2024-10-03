import os
import subprocess
from typing import Any, Optional, Type

from dotenv import load_dotenv
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from schemas.cli_command_schema import AWSCLICommand
from tools.base_aws_cli_tool import AWSCLITool

load_dotenv()


class AWSCLIGetToolParams(BaseModel):
    aws_cli_command: str = Field(..., description="AWS CLI command to retrieve data, e.g., 'ec2 describe-instances'")
    additional_args: Optional[str] = Field(None, description="Additional arguments to pass to the AWS CLI command")


class AWSCLIGetTool(AWSCLITool):
    name: str = "aws_cli_get_tool"
    description: str = (
        "This tool retrieves data from your AWS account using AWS CLI commands. "
        "Use the format `aws <command> <subcommand> [parameters]` to specify the data you want to retrieve."
    )
    args_schema: Type[AWSCLIGetToolParams] = AWSCLIGetToolParams

    def _run(
        self,
        aws_cli_command: str,
        additional_args: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs: Any,
    ) -> Any:
        if not aws_cli_command.startswith("aws "):
            aws_cli_command = f"aws {aws_cli_command}"
        if additional_args:
            aws_cli_command += f" {additional_args}"
        return super()._run(aws_cli_command, run_manager, **kwargs)


@tool("aws_cli_get_tool", args_schema=AWSCLICommand)
def aws_cli_get_tool(aws_cli_command: str):
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
    print("=======================", stdout, stderr)
    if my_process.returncode != 0:
        return f"status: error,\nmessage: {stderr}"
    return f"status: success,\nmessage: {stdout}"
