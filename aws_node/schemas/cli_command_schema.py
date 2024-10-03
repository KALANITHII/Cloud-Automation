from langchain.pydantic_v1 import BaseModel, Field, validator


class AWSCLICommand(BaseModel):
    aws_cli_command: str = Field(description="AWS CLI Command.")

    @validator('aws_cli_command')
    def must_start_with_aws(cls, v):
        if not v.startswith('aws'):
            raise ValueError('The command must start with "aws"')
        return v
