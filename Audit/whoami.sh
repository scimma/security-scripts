# get logged user
me=`aws sts get-caller-identity --output json | jq -r '.Arn'`

echo $me