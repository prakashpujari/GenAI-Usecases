from typing import TypedDict
from agent.planner import planner_agent
from agent.tools import tool_agent

class AgentState(TypedDict):
    input: str
    user: str
    role: str
    plan: str
    tool_result: str
    output: str

def run_agent(user_input, user, role):
    state = {"input": user_input, "user": user, "role": role}

    state.update(planner_agent(state))
    state.update(tool_agent(state))

    return state.get("tool_result", "No result")
