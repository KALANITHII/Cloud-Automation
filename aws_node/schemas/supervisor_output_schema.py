from pydantic import BaseModel, Field


class AWSActionQuery(BaseModel):
    is_aws_action: bool = Field(..., description="Indicates if the user's query is related to AWS resource actions")
