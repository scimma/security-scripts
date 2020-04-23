# aws configure must be set to json output
# needs: jq installed
# borrowed and modified from https://blog.datasyndrome.com/howto-terminate-all-ec2-instances-in-all-aws-regions-5213302ffa92
# temporary script to not mess with ongoing development
echo "$0 temporarily disabled"
exit 0

for region in `aws ec2 describe-regions | jq -r .Regions[].RegionName`
do
  echo "Stopping region $region..."
  aws ec2 describe-instances --region $region | \
    jq -r .Reservations[].Instances[].InstanceId | \
      xargs -L 1 -I {} aws ec2 modify-instance-attribute \
        --region $region \
        --no-disable-api-termination \
        --instance-id {}
  aws ec2 describe-instances --region $region | \
    jq -r .Reservations[].Instances[].InstanceId | \
      xargs -L 1 -I {} aws ec2 stop-instances \
        --region $region \
        --instance-id {}
done
