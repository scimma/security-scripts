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


echo "AWS reported the following roles existing:"
aws iam list-roles --output json --profile $profile | jq -r '.Roles[] | "ROLE: " + .RoleName + " DESCRIPTION: " + .Description'
