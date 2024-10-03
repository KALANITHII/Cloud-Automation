import io
import sys
from typing import Type

from azure.cli.core import get_default_cli
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class AzureCliInput(BaseModel):
    command: str = Field(..., description="The Azure CLI command to run")


class AzureCliTool(BaseTool):
    name = "azure_cli_tool"
    description = "Run Azure CLI commands and get the output"
    args_schema: Type[AzureCliInput] = AzureCliInput

    def _run(self, command: str) -> str:
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()

        # Run the Azure CLI command
        az_cli = get_default_cli()
        exit_code = az_cli.invoke(command.split())

        # Restore stdout
        sys.stdout = old_stdout

        # Get the output
        output = buffer.getvalue()

        if exit_code != 0:
            return f"Error executing command. Exit code: {exit_code}\nOutput: {output}"
        return output

    def _arun(self, command: str):
        # This tool doesn't support async, so we just call the sync version
        return self._run(command)
