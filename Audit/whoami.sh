# get logged user
me=`aws sts get-caller-identity | jq -r '.Arn'`

echo $me