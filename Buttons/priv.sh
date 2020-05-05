role=scimma_test_power_user

printHelp () {
cat - <<EOF
run a program in various modes
    ./debug.sh program
Options
   -h     print help and exit
   -x     debugme : turn on shell tracing (e.g. set -x)
   -r     role to deprivilege (default: ${role})
EOF
}

# option processing  $OPTARG fetches the argument
while getopts hxr: opt
do
  case "$opt" in
      h) printHelp ; exit 0 ;;
      x) set -x ;;
      r) role=$OPTARG ;;
      $\*?) printHelp; exit 1 ;;
  esac;
done


for policy in `aws iam list-attached-role-policies --role-name scimma_test_power_user | jq -r ".AttachedPolicies[].PolicyArn"`
do
  echo "Detaching $policy..."
  aws iam detach-role-policy --role-name $role --policy-arn $policy
done

echo "Attaching ProposedPoweruser and RoleManagementWithCondition to $role"
aws iam attach-role-policy --role-name $role --policy-arn arn:aws:iam::585193511743:policy/ProposedPoweruser
aws iam attach-role-policy --role-name $role --policy-arn arn:aws:iam::585193511743:policy/RoleManagementWithCondition
