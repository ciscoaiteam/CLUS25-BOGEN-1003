from functools import lru_cache
from langchain_anthropic import ChatAnthropic # type: ignore
from langchain_openai import ChatOpenAI
from my_agent.utils.tools import tools
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage
import logging

logger = logging.getLogger(__name__)

@lru_cache(maxsize=4)
def _get_model(model_name: str):
    if model_name == "openai":
        model = ChatOpenAI(temperature=0, model_name="gpt-4o")
    elif model_name == "anthropic":
        model =  ChatAnthropic(temperature=0, model_name="claude-3-7-sonnet-20250219")
    else:
        raise ValueError(f"Unsupported model type: {model_name}")

    model = model.bind_tools(tools)
    return model


def should_continue(state):
    logger.info("Entering should_continue function.")
    messages = state["messages"]
    last_message = messages[-1]
    
    if not last_message.tool_calls:
        logger.info("No tool calls found in the last message. Returning 'end'.")
        return "end"

    tool_call = last_message.tool_calls[0]

    # If it's a dict, extract the name safely
    if isinstance(tool_call, dict):
        tool_name = tool_call.get("name")
    else:
        tool_name = tool_call.name

    logger.info(f"Tool name extracted: {tool_name}")

    if tool_name in ["FirmwareAudit", "UpgradePlan", "ITSMApproval"]:
        return tool_name
    else:
        logger.warning(f"Unexpected tool call: {tool_name}. Ending execution.")
        return "end"


system_prompt = """You are a network automation assistant specializing in Cisco Nexus firmware upgrades.

WORKFLOW STEPS (must be followed in order):

1. **FIRMWARE AUDIT**: First, call the 'FirmwareAudit' tool to get the list of devices with outdated firmware.

2. **UPGRADE PLANNING**: After receiving the audit results, call the 'UpgradePlan' tool and pass the EXACT JSON output from the FirmwareAudit tool as the devices_json parameter. This will return:
   - devices: The original device list
   - itsm_changemanagement_items: Planned changes that might conflict
   - itsm_outage_items: Current outages that might impact upgrades
   - itsm_knowledgebase_items: Relevant KB articles

3. **ANALYSIS & PLANNING**: Once you have the UpgradePlan data, analyze it and create a structured upgrade plan by:
   - Cross-referencing each device against change management items
   - Checking for outage conflicts
   - Noting relevant KB articles
   - Prioritizing Spine devices first (2-hour windows), then Leaf devices (1-hour windows)
   - Scheduling sequentially with no overlaps

4. **APPROVAL SUBMISSION**: Finally, call the 'ITSMApproval' tool with your complete upgrade plan.

CRITICAL RULES:
- Always pass the COMPLETE JSON output from FirmwareAudit to UpgradePlan
- Never call UpgradePlan without the devices_json parameter
- Create your upgrade plan analysis using reasoning, not tool calls
- Include specific timing, priorities, and conflict information in your final plan

UPGRADE PLAN FORMAT:
For each device include:
- Priority order (Spine devices first)
- Maintenance window (2hrs for Spine, 1hr for Leaf)
- Change management conflicts (if any)
- Outage impacts (if any)
- Relevant KB notes
- Upgrade steps summary

If there are conflicts or issues that prevent upgrades, clearly document why each affected device cannot be upgraded at this time.
"""

# Define the function that calls the model
def call_model(state, config):
    logger.info("Entering call_model function.")
    # Get the current messages from the state
    current_messages = state["messages"]
    logger.debug(f"Current messages: {current_messages}")
    # Create a SystemMessage object for the system prompt
    system_message = SystemMessage(content=system_prompt)
    # Prepend the SystemMessage, ensuring a consistent list of BaseMessage objects
    messages_with_system = [system_message] + list(current_messages)
    logger.debug(f"Messages being sent to model: {messages_with_system}")
    # Catch incase the LangSmith Assistent Model is blank ( LangSmith UI - Assistant )
    configurable = config.get('configurable', {}) if config else {}
    model_name = configurable.get("model_name") or "anthropic"
    logger.info(f"Using model: {model_name}")
    model = _get_model(model_name)
    response = model.invoke(messages_with_system)
    logger.info(f"Model response received. Type: {type(response)}")
    logger.debug(f"Model response content: {response}")
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}