#!/bin/sh
# target role check script

# defaults
role=scimma_power_user
profile=scimma-uiuc-aws-admin


printHelp () {
# help function
cat - <<EOF
DESCRIPTION
   List policies attached to a specified role
OPTIONS
   -h     print help and exit
   -x     debugme: turn on shell tracing (e.g. set -x)
   -r     role to check (default: ${role})
   -p     CLI profile to use (default: ${profile})
EOF
}

# option processing, $OPTARG fetches the argument
while getopts hxr:p: opt
do
  case "$opt" in
      h) printHelp; exit 0 ;;
      x) set -x ;;
      r) role=$OPTARG ;;
      p) profile=$OPTARG ;;
      $\*?) printHelp; exit 1 ;;
  esac;
done

# echo and list policies
echo "$role role reported the following policies attached:"
aws iam list-attached-role-policies --role-name $role --output json --profile $profile | jq -r ".AttachedPolicies[].PolicyName"