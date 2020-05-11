# defaults
profile=scimma-uiuc-aws-admin

printHelp () {
cat - <<EOF
run a program in various modes
    ./debug.sh program
Options
   -h     print help and exit
   -x     debugme : turn on shell tracing (e.g. set -x)
   -p     CLI profile to use (default: ${profile})
EOF
}

# get profile
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

# run test
test=`aws iam simulate-principal-policy --policy-source-arn $me --action-names "iam:DetachRolePolicy" \
"iam:AttachRolePolicy" "ec2:DescribeRegions" "ec2:StopInstances" "ec2:ModifyInstanceAttribute" "sts:GetCallerIdentity" \
 --output json --profile $profile`

# print output
echo $test | jq -r '.EvaluationResults[] | .EvalActionName + " [" + .EvalDecision + "]"'