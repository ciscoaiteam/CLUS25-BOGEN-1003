from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import Tool

# Initialize the base search tool once
_tavily_search = TavilySearchResults(max_results=2) # Increased max_results slightly

# Define specific functions for each task
def search_weather(query: str) -> str:
    """Searches for weather forecasts."""
    return _tavily_search.invoke(f"Weather forecast for {query}")

def search_activities(query: str) -> str:
    """Searches for activities, attractions, or things to do."""
    return _tavily_search.invoke(f"Things to do or activities in {query}")

def search_flights(query: str) -> str:
    """Searches for flight information."""
    return _tavily_search.invoke(f"Flights for {query}")

# Create tools from the functions
weather_tool = Tool.from_function(
    func=search_weather,
    name="WeatherSearch",
    description="Useful for finding weather forecasts for a specific location and time.",
)

activity_tool = Tool.from_function(
    func=search_activities,
    name="ActivitySearch",
    description="Useful for finding activities, attractions, or things to do in a specific location.",
)

flight_tool = Tool.from_function(
    func=search_flights,
    name="FlightSearch",
    description="Useful for finding flight information to a specific location around a certain time.",
)

tools = [weather_tool, activity_tool, flight_tool]