import yaml
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from plan.system_prompt import get_system_message
from schemas.cli_parameter_schema import Params
from tools import AWSCLIGetTool

load_dotenv()

with open("config.yaml", "r") as file:
    config_data = yaml.safe_load(file)

planner_agent_runnable = get_system_message | ChatOpenAI(
    model_name=config_data["planner_agent_config"]["model_name"],
    temperature=config_data["planner_agent_config"]["temperature"],
).bind_tools([Params, AWSCLIGetTool()])
