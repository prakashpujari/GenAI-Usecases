def planner_agent(state):
    role = state["role"]

    if role == "PRODUCT_OWNER":
        plan = "create ticket"
    else:
        plan = "view ticket"

    return {"plan": plan}
