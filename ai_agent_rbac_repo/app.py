# Entry point for Lambda / local
from agent.graph import run_agent

if __name__ == "__main__":
    response = run_agent("create jira ticket", user="alice@company.com", role="PRODUCT_OWNER")
    print(response)
