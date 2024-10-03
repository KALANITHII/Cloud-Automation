from typing import List, Optional

from langchain_core.pydantic_v1 import BaseModel, Field


class SubFields(BaseModel):
    key: str = Field(description="The name of the parameter.")
    description: str = Field(description="A short description of the parameter.")
    value: str = Field(description="The value provided by the user.")


class Params(BaseModel):
    """
    Schema to collect required and optional parameters for a user's request to perform an action in AWS.

    Attributes:
        user_request (str): The action that the user wants to perform.
        required_params (List[SubFields]): Required parameters for the AWS CLI command.
        optional_params (List[SubFields]): Optional parameters for the AWS CLI command.
    """
    user_request: str = Field(description="The action that the user wants to perform.")
    required_params: List[SubFields] = Field(description="Required parameters for the AWS CLI command.")
    optional_params: Optional[List[SubFields]] = Field(..., description="Optional parameters for the AWS CLI command.")
