# aws configure must be set to json output
# needs: jq installed
# borrowed and modified from https://blog.datasyndrome.com/howto-terminate-all-ec2-instances-in-all-aws-regions-5213302ffa92
# temporary script to not mess with ongoing development

# get logged user
me=`aws sts get-caller-identity --output json | jq -r '.Arn'`

# run test
test=`aws iam simulate-principal-policy --policy-source-arn $me --action-names "ec2:DescribeRegions" \
"ec2:StopInstances" "ec2:ModifyInstanceAttribute" --output json`

regions=`echo $test | jq -r '.EvaluationResults[] | select(.EvalActionName=="ec2:DescribeRegions") | .EvalDecision'`
stopin=`echo $test | jq -r '.EvaluationResults[] | select(.EvalActionName=="ec2:StopInstances") | .EvalDecision'`
modattr=`echo $test | jq -r '.EvaluationResults[] | select(.EvalActionName=="ec2:ModifyInstanceAttribute") | .EvalDecision'`

echo "ec2:DescribeRegions simulation result: $regions"
for region in `aws ec2 describe-regions --output json | jq -r .Regions[].RegionName`
do
  echo "Stopping region $region..."
  sleep 1
  echo "ec2:StopInstances simulation result: $stopin"
  echo "ec2:ModifyInstanceAttribute simulation result: $modattr"
done
