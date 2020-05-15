#!/bin/sh
# AWS Roles listing script

# defaults
profile=scimma-uiuc-aws-admin


printHelp () {
# help function
cat - <<EOF
DESCRIPTION
   List existing AWS Roles
OPTIONS
   -h     print help and exit
   -x     debugme: turn on shell tracing (e.g. set -x)
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

# echo and list roles
echo "AWS reported the following roles existing:"
aws iam list-roles --output json --profile $profile | jq -r '.Roles[] | "ROLE: " + .RoleName + " DESCRIPTION: " + .Description'
