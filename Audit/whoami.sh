#!/bin/sh
# current user ARN retrieving script

# defaults
profile=scimma-uiuc-aws-admin


printHelp () {
# help script
cat - <<EOF
DESCRIPTION
   Retrieve the IAM of the current CLI logon
OPTIONS
   -h     print help and exit
   -x     debugme: turn on shell tracing (e.g. set -x)
   -p     CLI profile to use (default: ${profile})
EOF
}

# option processing, $OPTARG fetches the argument
while getopts hxp: opt
do
  case "$opt" in
      h) printHelp ; exit 0 ;;
      x) set -x ;;
      p) profile=$OPTARG ;;
      $\*?) printHelp; exit 1 ;;
  esac;
done

# get logged user
me=`aws sts get-caller-identity --output json --profile $profile | jq -r '.Arn'`
echo $me