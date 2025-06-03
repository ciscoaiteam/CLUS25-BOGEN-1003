# Development Mode - Allows me to run this workflow locally
import os
from os.path import join, dirname
import platform

# Development Mode - Only load dotenv on Windows machines; Only used for local deployments
'''You will need to have a .env file in the my_agent folder with the correct 
ANTHROPIC_API_KEY=...
TAVILY_API_KEY=...
OPENAI_API_KEY=...
LANGSMITH_API_KEY=...
LANGSMITH_TRACING=true
LANGSMITH_TRACING=...
'''
if platform.system() == "Windows":
    from dotenv import load_dotenv
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)


# Application Imports
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from my_agent.utils.nodes import call_model, should_continue
from my_agent.utils.state import AgentState
from my_agent.utils.tools import weather_tool, activity_tool, flight_tool
from typing import TypedDict, Literal
import logging


# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the config
class GraphConfig(TypedDict):
    model_name: Literal["anthropic", "openai"]

# Define a new graph
workflow = StateGraph(AgentState, config_schema=GraphConfig)
logger.info("Initialized StateGraph with AgentState and GraphConfig.")

# Define the agent node
workflow.add_node("agent", call_model)
logger.info("Added node: agent")

# Define individual nodes for each tool
weather_action_node = ToolNode([weather_tool])
activity_action_node = ToolNode([activity_tool])
flight_action_node = ToolNode([flight_tool])
workflow.add_node("weather_action", weather_action_node)
workflow.add_node("activity_action", activity_action_node)
workflow.add_node("flight_action", flight_action_node)

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.set_entry_point("agent")
logger.info("Set entry point to: agent")

# We now add a conditional edge
workflow.add_conditional_edges(
    # First, we define the start node. We use `agent`.
    # This means these are the edges taken after the `agent` node is called.
    "agent",
    # Next, we pass in the function that will determine which node is called next.
    should_continue,
    # Finally we pass in a mapping.
    # The keys are the names of the tools (or 'end'), and the values are the names of the nodes to route to.
    # END is a special node marking that the graph should finish.
    # What will happen is we will call `should_continue`, and then the output of that
    # will be matched against the keys in this mapping.
    # Based on which one it matches, that node will then be called.
    {
        "WeatherSearch": "weather_action",
        "ActivitySearch": "activity_action",
        "FlightSearch": "flight_action",
        # Otherwise we finish.
        "end": END,
    },
)
logger.info("Added conditional edges from 'agent' based on 'should_continue'.")
# We now add a normal edge from `tools` to `agent`.
# This means that after `tools` is called, `agent` node is called next.
workflow.add_edge("weather_action", "agent")
workflow.add_edge("activity_action", "agent")
workflow.add_edge("flight_action", "agent")


# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable
graph = workflow.compile()
logger.info("Workflow compiled successfully.")
