# ✈️ Demo 2: Vacation Planner (Conversational AI)

## 📘 Overview

This LangGraph Studio project demonstrates an AI-powered assistant designed to streamline and automate the process of vacation planning. The agent intelligently gathers information about weather, activities, and flights, formulates a detailed trip plan, and presents it to the user. This project showcases the power of AI agents, tool usage, and iterative workflows in a real-world scenario, making it an excellent demonstration for presentations on Agent and Tool calls and iterative workflow capabilities. This demo requires a LangSmith Login.

Langgraph Studio URL [Link](https://smith.langchain.com/studio/thread?baseUrl=https%3A%2F%2Fclus25-demo02-v3-64e5e70f82cf508bb3f81314cb16a39c.us.langgraph.app)
- Backup Langgraph Studio URL [Link](https://smith.langchain.com/studio/thread?baseUrl=https%3A%2F%2Fclus25-demo02-v3-64e5e70f82cf508bb3f81314cb16a39c.us.langgraph.app)
> Please plan a trip to Paris, Texas for 5 days with my family in August.  We will be leaving from San Joes, CA

## ✨ Features & Functions

This assistant leverages a stateful graph defined in `agent.py` to manage a multi-step workflow. It interacts with external services via tools defined in `tools.py` and is guided by a sophisticated system prompt and logic within `nodes.py`.

1.  **Intelligent Agent Core (`nodes.py`, `agent.py`):**

    *   **Iterative Processing:** The agent operates in a loop. It calls tools, processes their outputs, and the `should_continue` function (in `nodes.py`) determines the next step in the workflow. This allows for a dynamic, responsive process.
    *   **LLM-Powered Reasoning:** Utilizes a Large Language Model (configurable for "anthropic" or "openai" as per `GraphConfig` in `agent.py`) to understand instructions from the `system_prompt`, process information from tools, and make planning decisions.
    *   **State Management (`state.py`):** Employs `AgentState` to maintain the conversation history (`messages`) as the process unfolds.
    *   **System Prompt Driven Behavior (`nodes.py`):** A detailed `system_prompt` guides the agent through a specific sequence of operations, defines critical rules, and specifies the desired output format for the vacation plan.

    ```mermaid
    graph TD;
        Agent-->Weather_Action;
        Agent-->Activity_Action;
        Agent-->Flight_Action;
        Weather_Action-->Agent;
        Activity_Action-->Agent;
        Flight_Action-->Agent;
    ```

2.  **Workflow Steps & Tool Integration:**

    *   **Step 1: Weather Search (`WeatherSearch` tool):**
        *   The workflow begins with the agent node, which, guided by the `system_prompt`, determines the need to call the `WeatherSearch` tool.
        *   **Functionality:** This tool (defined in `tools.py/search_weather()`) uses Tavily Search to find weather forecasts for a specific location and time.
        *   **Graph Node:** `weather_action` in `agent.py`.

    *   **Step 2: Activity Search (`ActivitySearch` tool):**
        *   After receiving the weather information, the agent calls the `ActivitySearch` tool.
        *   **Functionality:** This tool (defined in `tools.py/search_activities()`) uses Tavily Search to find activities, attractions, or things to do in a specific location.
        *   **Graph Node:** `activity_action` in `agent.py`.

    *   **Step 3: Flight Search (`FlightSearch` tool):**
        *   After gathering activity information, the agent calls the `FlightSearch` tool.
        *   **Functionality:** This tool (defined in `tools.py/search_flights()`) uses Tavily Search to find flight information to a specific location around a certain time.
        *   **Graph Node:** `flight_action` in `agent.py`.

    *   **Step 4: AI-Driven Plan Creation (Agent Reasoning):**
        *   As mandated by the `system_prompt` (in `nodes.py`), the agent performs an in-depth analysis of the combined data from the `WeatherSearch`, `ActivitySearch`, and `FlightSearch` tools. This critical step utilizes the LLM's reasoning capabilities, not a separate tool.
        *   **Analysis includes:**
            *   Synthesizing weather information to suggest appropriate clothing or gear.
            *   Identifying potential activities based on the trip's duration and the user's interests.
            *   Providing flight options and estimated costs.
        *   **Output:** The agent formulates a structured, comprehensive vacation plan.

3.  **Critical Operational Rules & Workflow Control (enforced by `system_prompt` and graph logic):**

    *   The `add_conditional_edges` in `agent.py` uses the `should_continue` function to route the workflow based on the last tool called or to end the process.
    *   Edges then route back from tool actions to the agent node, enabling the iterative nature of the workflow.
    *   The agent is instructed to call the tools ONE AT A TIME in the specified order.

### 🛠️ Self-Deployment Guide

To deploy this Vacation Planner yourself using LangSmith Platform, follow these steps:

1.  **Clone the Project:** Clone the contents of this project folder (containing `agent.py`, `nodes.py`, `tools.py`, `state.py`, etc.) to your local machine. It's recommended to then push this project to your own Git repository (e.g., on GitHub, GitLab) for easier integration with LangSmith.

2.  **Obtain API Keys:** You will need the following API keys. These should be set as environment variables in your LangSmith deployment environment or your local environment if testing locally.

    *   `ANTHROPIC_API_KEY`: Required for using Anthropic's language models (e.g., Claude Sonnet). The `nodes.py` file is configured to potentially use Anthropic models, and `call_model` defaults to "anthropic" if no model is specified in the graph config.
    *   `OPENAI_API_KEY` (Optional): If you plan to configure the agent to use OpenAI models (e.g., GPT-4o) as supported in `nodes.py`.
    *   `TAVILY_API_KEY`: Required for the `TavilySearchResults` used in `tools.py`.

3.  **Deploy via LangSmith Platform:**

    *   Ensure your project (the cloned folder content) is in a Git repository accessible by LangSmith.
    *   Navigate to your LangSmith account and follow the platform's documentation to deploy a new LangGraph agent or application from your Git repository.
    *   During the LangSmith deployment configuration:
        *   Point LangSmith to your repository and specify the main branch or file that exposes the compiled LangGraph (e.g., `agent.graph` from `agent.py`).
        *   Set the necessary environment variables in your LangSmith deployment settings (e.g., `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, and `TAVILY_API_KEY`).
    *   Once deployed, LangSmith will provide an endpoint or interface to interact with your agent.

### 🚀 Potential Expansions & Future Enhancements

The current project provides a solid foundation for a vacation planning assistant. Here’s how its features could be significantly expanded upon:

1.  **Real-World Integration:**

    *   **Live Data Sources:**
        *   Integrate with real-time flight booking APIs (e.g., Expedia, Skyscanner) to provide up-to-date flight prices and availability.
        *   Connect to hotel booking APIs (e.g., Booking.com, Hotels.com) to suggest accommodations based on user preferences and budget.
        *   Use real-time weather APIs to provide more accurate and localized weather forecasts.

2.  **Personalization & Customization:**

    *   **User Profiles:** Allow users to create profiles with their preferences (e.g., interests, budget, travel style) to personalize the vacation plans.
    *   **Preference Learning:** Implement mechanisms for the agent to learn from user feedback and adjust its recommendations accordingly.

3.  **Advanced Planning Capabilities:**

    *   **Itinerary Optimization:** Optimize the itinerary based on factors such as travel time, cost, and user preferences.
    *   **Multi-Destination Planning:** Support planning trips with multiple destinations.
    *   **Integration with Calendar & Reminders:** Allow users to add planned activities to their calendars and set reminders.

4.  **Enhanced Human-in-the-Loop Interaction:**

    *   **Interactive Plan Refinement:** Provide a mechanism for users to review, modify, or annotate the AI-generated vacation plan.
    *   **Visualizations:** Use maps and other visualizations to enhance the user experience.

5.  **Broader Scope & Increased Intelligence:**

    *   **Travel Restrictions & Advisories:** Integrate with APIs that provide information on travel restrictions and advisories.
    *   **Language Support:** Support multiple languages.

This Vacation Planner project effectively demonstrates a significant step towards AI-augmented vacation planning. By building upon its current foundation, it can evolve into an even more powerful tool, promising substantial improvements in efficiency and convenience for users.
