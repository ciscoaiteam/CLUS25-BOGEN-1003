from functools import lru_cache
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from my_agent.utils.tools import tools
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage
import logging

logger = logging.getLogger(__name__)

'''
OPEN_AI_KEY = {"key is a variable in the deployment"}
ANTHROPIC_API_KEY = {"key is a variable in the deployment"}
TAVILY_API_KEY = {"key is a variable in the deployment"}
You don't need to have all 2 AI as a service vendors to run this lab, but I wanted to give the option.
'''

@lru_cache(maxsize=4)
def _get_model(model_name: str):
    '''Primary Open AI model with a Anthropic Failover - This could be a local vLLM installation.
       This function allows for the Langraph Studio Assistant to select used model.
    '''
    if model_name == "openai":
        model = ChatOpenAI(temperature=0, model="gpt-4.1")
    elif model_name == "anthropic":
        model =  ChatAnthropic(temperature=0, model="claude-3-7-sonnet-latest")
    else:
        # Failover incase a model wasn't selected in the Studio Assistant and try to use this as a default.
        model = ChatOpenAI(temperature=0, model="gpt-4.1")
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

Once you have gathered information from all three tools, synthesize the results into a comprehensive plan for the user.

!Important: Only provide information that pertains to planning this trip.  No other topics should be referenced.
"""


# Define the function that calls the model
def call_model(state, config):
    logger.info("Entering call_model function.")
    
    # Get the current messages from the state
    current_messages = state.get("messages", [])
    logger.debug(f"Current messages count: {len(current_messages)}")
    
    # Create system message
    system_message = SystemMessage(content=system_prompt)
    messages_with_system = [system_message] + list(current_messages)
    
    # Get model configuration
    configurable = config.get('configurable', {}) if config else {}
    model_name = configurable.get("model_name", "openai")
    logger.info(f"Using model: {model_name}")
    
    try:
        model = _get_model(model_name)
        logger.info(f"Model loaded successfully: {model}")
        
        response = model.invoke(messages_with_system)
        logger.info(f"Model response received. Type: {type(response)}")
        logger.debug(f"Response has tool_calls: {hasattr(response, 'tool_calls') and bool(response.tool_calls)}")
        
        return {"messages": [response]}
        
    except Exception as e:
        logger.error(f"Error in call_model: {str(e)}")
        raise
