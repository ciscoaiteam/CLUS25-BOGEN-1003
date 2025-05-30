from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
from typing import TypedDict, Annotated, Sequence, Optional

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    devices: Optional[list[str]]
    upgrade_plan: Optional[str]
    approval_status: Optional[str]
