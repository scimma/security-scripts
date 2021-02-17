t_self = """
[
    {
        "my_service": "iam",
        "my_function": "list_groups",
        "path": ".[].Groups[].GroupName",
        "peer_service": "group",
        "is_self": true
    },
    {
        "my_service": "iam",
        "my_function": "list_roles",
        "path": ".[].Roles[].RoleName",
        "peer_service": "role",
        "is_self": true
    },
    {
        "my_service": "iam",
        "my_function": "list_users",
        "path": ".[].Users[].UserName",
        "peer_service": "user",
        "is_self": true
    },
    
    
    {
        "my_service": "iam",
        "my_function": "list_attached_user_policies",
        "path": ".[].AttachedPolicies[].PolicyName",
        "peer_service": "policy",
        "is_self": true
    },
    {
        "my_service": "iam",
        "my_function": "list_attached_group_policies",
        "path": ".[].AttachedPolicies[].PolicyName",
        "peer_service": "policy",
        "is_self": true
    },
    {
        "my_service": "iam",
        "my_function": "list_attached_role_policies",
        "path": ".[].AttachedPolicies[].PolicyName",
        "peer_service": "policy",
        "is_self": true
    }
    
]
"""

t_others = """
[
    {
        "my_service": "iam",
        "my_function": "list_attached_user_policies",
        "path": ".[].UserName",
        "peer_service": "user",
        "is_self": false
    },
    {
        "my_service": "iam",
        "my_function": "list_attached_group_policies",
        "path": ".[].GroupName",
        "peer_service": "group",
        "is_self": false
    },
    {
        "my_service": "iam",
        "my_function": "list_attached_role_policies",
        "path": ".[].RoleName",
        "peer_service": "role",
        "is_self": false
    }
]
"""