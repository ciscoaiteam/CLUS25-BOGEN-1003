from functools import lru_cache
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from my_agent.utils.tools import tools
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage
import logging

logger = logging.getLogger(__name__)

@lru_cache(maxsize=4)
def _get_model(model_name: str):
    if model_name == "openai":
        logger.debug("Using OpenAI model.")
        model = ChatOpenAI(temperature=0, model_name="gpt-4o")
    elif model_name == "anthropic":
        logger.debug("Using Anthropic model.")
        model =  ChatAnthropic(temperature=0, model_name="claude-3-7-sonnet-latest")
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

    if tool_name in ["WeatherSearch", "ActivitySearch", "FlightSearch"]:
        return tool_name
    else:
        logger.warning(f"Unexpected tool call: {tool_name}. Ending execution.")
        return "end"


system_prompt = """You are a helpful vacation planning assistant.
Your goal is to help the user plan their trip based on their request.
The user will provide a destination, a start time (which might be relative, like 'in 10 days'), and a duration (e.g., 'for 5 days').

To fulfill the request, you MUST use the available tools in the following order:
1. First, use the 'WeatherSearch' tool to find the weather forecast for the destination around the specified start date.
2. Second, use the 'ActivitySearch' tool to find potential things to do or sights to see at the destination suitable for the trip's duration.
3. Third, use the 'FlightSearch' tool to find information about available flights to the destination around the specified start date.

IMPORTANT: You must call the tools ONE AT A TIME in the specified order. Wait for the result of one tool call before making the next one.

Once you have gathered information from all three tools, synthesize the results into a comprehensive plan for the user."""

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

# Define individual tool nodes (though they won't be directly used here,
# the tools list is used for binding in _get_model)
# tool_node = ToolNode(tools) # No longer needed here for graph definition
