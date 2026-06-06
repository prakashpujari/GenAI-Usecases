ROLE_PERMISSIONS = {
    "ADMIN": ["create", "read", "update", "delete"],
    "PRODUCT_OWNER": ["create", "read", "update"],
    "DEVELOPER": ["read", "update"],
    "VIEWER": ["read"]
}

USER_ROLES = {
    "alice@company.com": "PRODUCT_OWNER",
    "bob@company.com": "DEVELOPER"
}

def check_permission(user, action):
    role = USER_ROLES.get(user)
    if action not in ROLE_PERMISSIONS.get(role, []):
        raise Exception("Access Denied")
