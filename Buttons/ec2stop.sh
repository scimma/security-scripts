# needs: jq installed
# borrowed and modified from https://blog.datasyndrome.com/howto-terminate-all-ec2-instances-in-all-aws-regions-5213302ffa92
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

# option processing  $OPTARG fetches the argument
while getopts hxp: opt
do
  case "$opt" in
      h) printHelp ; exit 0 ;;
      x) set -x ;;
      p) profile=$OPTARG ;;
      $\*?) printHelp; exit 1 ;;
  esac;
done

# temporary script to not mess with ongoing development
echo "$0 temporarily disabled"
exit 0

for region in `aws ec2 describe-regions --output json --profile $profile | jq -r .Regions[].RegionName`
do
  echo "Stopping region $region..."
  aws ec2 describe-instances --region $region --output json --profile $profile | \
    jq -r .Reservations[].Instances[].InstanceId | \
      xargs -L 1 -I {} aws ec2 modify-instance-attribute \
        --region $region \
        --no-disable-api-termination \
        --instance-id {} \
        --output json \
        --profile $profile
  aws ec2 describe-instances --region $region --output json --profile $profile | \
    jq -r .Reservations[].Instances[].InstanceId | \
      xargs -L 1 -I {} aws ec2 stop-instances \
        --region $region \
        --instance-id {} \
        --output json \
        --profile $profile
done
