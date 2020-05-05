
aws iam list-roles --output json | jq -r '.Roles[] | "ROLE: " + .RoleName + " DESCRIPTION: " + .Description'
