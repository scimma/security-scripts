#!/bin/sh
# active CLI user sufficient privilege check

# defaults
profile=scimma-uiuc-aws-admin


printHelp () {
# help function
cat - <<EOF
DESCRIPTION
   Check if the current CLI user has sufficient privileges
OPTIONS
   -h     print help and exit
   -x     debugme: turn on shell tracing (e.g. set -x)
   -p     CLI profile to use (default: ${profile})
EOF
}

# option processing, $OPTARG fetches the argument
while getopts hxp: opt
do
  case "$opt" in
      h) printHelp ; exit 0 ;;
      x) set -x ;;
      p) profile=$OPTARG ;;
      *) printHelp; exit 1 ;;
  esac;
done

# get logged user
me=`aws sts get-caller-identity --output json --profile $profile | jq -r '.Arn'`

# run simulations
test=`aws iam simulate-principal-policy --policy-source-arn $me --action-names "iam:DetachRolePolicy" \
"iam:AttachRolePolicy" "ec2:DescribeRegions" "ec2:StopInstances" "ec2:ModifyInstanceAttribute" "sts:GetCallerIdentity" \
 --output json --profile $profile`

# print results
echo $test | jq -r '.EvaluationResults[] | .EvalActionName + " [" + .EvalDecision + "]"'