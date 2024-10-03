from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import PydanticOutputParser

from schemas.supervisor_output_schema import AWSActionQuery

system_message = """Your job is to check whether user is asking for any action related to AWS resources e.g. create, update, delete, read etc."
- You can ignore grammar mistake and decide it irrespective of spelling or grammar mistakes done by user.

Conditions:
- return true if user is asking to related to AWS resources ACTIONS mentioned above.
- return false in case of general queries or questions.

Format Instructions:
- {format_instructions}
"""

parser = PydanticOutputParser(pydantic_object=AWSActionQuery)


def get_system_message(messages):
    return [
        SystemMessage(content=system_message.format(format_instructions=parser.get_format_instructions()))] + messages
