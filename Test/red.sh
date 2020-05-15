#!/bin/sh
# simulate getting the red button engaged
role=scimma_test_power_user
profile=scimma-uiuc-aws-admin

printHelp () {
# help script
cat - <<EOF
DESCRIPTION
   RED button simulation that checks if the CLI user has correct permissions
OPTIONS
   -h     print help and exit
   -x     debugme : turn on shell tracing (e.g. set -x)
   -r     role to deprivilege (default: ${role})
   -p     CLI profile to use (default: ${profile})
EOF
}

# option processing, $OPTARG fetches the argument
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

# echo real text and simulate policy detachment policy
echo "Stripping $role of ProposedPoweruser and attaching ReadOnlyAccess"
me=`aws sts get-caller-identity --output json --profile $profile | jq -r '.Arn'`
test=`aws iam simulate-principal-policy --policy-source-arn $me --action-names "iam:DetachRolePolicy" \
"iam:AttachRolePolicy" --output json --profile $profile`

# print output
echo $test | jq -r '.EvaluationResults[] | .EvalActionName + " simulation result: " + .EvalDecision'




