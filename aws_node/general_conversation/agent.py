import yaml
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from .system_prompt import get_system_message

load_dotenv()

with open("config.yaml", "r") as file:
    config_data = yaml.safe_load(file)

general_conversation_agent_runnable = get_system_message | ChatOpenAI(
    model_name=config_data["general_conversation_agent_config"]["model_name"],
    temperature=config_data["general_conversation_agent_config"]["temperature"],
)
