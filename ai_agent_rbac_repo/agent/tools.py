from security.rbac import check_permission

def tool_agent(state):
    user = state["user"]
    plan = state["plan"]

    if "create" in plan:
        check_permission(user, "create")
        return {"tool_result": "Ticket created successfully"}

    elif "view" in plan:
        check_permission(user, "read")
        return {"tool_result": "Viewing ticket"}
