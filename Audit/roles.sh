
aws iam list-roles | jq -r '.Roles[] | "ROLE: " + .RoleName + " DESCRIPTION: " + .Description'
