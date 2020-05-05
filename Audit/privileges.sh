# get logged user
me=`aws sts get-caller-identity --output json | jq -r '.Arn'`

# run test
test=`aws iam simulate-principal-policy --policy-source-arn $me --action-names "iam:DetachRolePolicy" \
"iam:AttachRolePolicy" "ec2:DescribeRegions" "ec2:StopInstances" "ec2:ModifyInstanceAttribute" "sts:GetCallerIdentity" \
 --output json`

# print output
echo $test | jq -r '.EvaluationResults[] | .EvalActionName + " [" + .EvalDecision + "]"'