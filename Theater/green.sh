# simulate getting the red button engaged

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

# is this sufficient? shall we detach everything instead?

echo "Stripping $role of ReadOnlyAccess and attaching ProposedPoweruser"
me=`aws sts get-caller-identity --output json | jq -r '.Arn'`
test=`aws iam simulate-principal-policy --policy-source-arn $me --action-names "iam:DetachRolePolicy" \
"iam:AttachRolePolicy" --output json`

# print output
echo $test | jq -r '.EvaluationResults[] | .EvalActionName + " simulation result: " + .EvalDecision'




