#!/bin/sh
# GREEN button reprivileging script

# defaults
role=scimma_test_power_user
profile=scimma-uiuc-aws-admin

printHelp () {
# help script
cat - <<EOF
DESCRIPTION
   Reinstate full acess to the specified role
OPTIONS
   -h     print help and exit
   -x     debugme : turn on shell tracing (e.g. set -x)
   -r     role to deprivilege (default: ${role})
   -p     CLI profile to use (default: ${profile})
EOF
}

# option processing  $OPTARG fetches the argument
while getopts hxr:p: opt
do
  case "$opt" in
      h) printHelp ; exit 0 ;;
      x) set -x ;;
      r) role=$OPTARG ;;
      p) profile=$OPTARG ;;
      $\*?) printHelp; exit 1 ;;
  esac;
done

# get attached policies and detach them in a loop
for policy in `aws iam list-attached-role-policies --role-name scimma_test_power_user --output json --profile $profile | jq -r ".AttachedPolicies[].PolicyArn"`
do
  echo "Detaching $policy..."
  aws iam detach-role-policy --role-name $role --policy-arn $policy --profile $profile
done

# attach full access
echo "Attaching ProposedPoweruser and RoleManagementWithCondition to $role"
aws iam attach-role-policy --role-name $role --policy-arn arn:aws:iam::585193511743:policy/ProposedPoweruser --profile $profile
aws iam attach-role-policy --role-name $role --policy-arn arn:aws:iam::585193511743:policy/RoleManagementWithCondition --profile $profile
