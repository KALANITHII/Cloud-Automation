import yaml
from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI

from schemas.supervisor_output_schema import AWSActionQuery
from .system_prompt import get_system_message

load_dotenv()

with open("config.yaml", "r") as file:
    config_data = yaml.safe_load(file)

parser = PydanticOutputParser(pydantic_object=AWSActionQuery)


def convert_to_base_message(parser_output: AWSActionQuery):
    print(parser_output)
    return [AIMessage(content=parser_output.is_aws_action)]


supervisor_agent_runnable = get_system_message | ChatOpenAI(
    model_name=config_data["supervisor_agent_config"]["model_name"],
    temperature=config_data["supervisor_agent_config"]["temperature"],
) | parser | convert_to_base_message
