#!/bin/sh
# installed third-party application check script


jqTest() {
# jq presence test function
  if hash jq 2>/dev/null; then
      echo "jq installed:  [  OK  ]"
  else
      echo "jq installed:  [FAILED]"
      echo "please install jq"
  fi
}


awsTest() {
# aws cli presence test function
  if hash aws 2>/dev/null; then
      echo "aws installed: [  OK  ]"
  else
      echo "aws installed: [FAILED]"
      echo "please install aws"
  fi
}

# run test functions
jqTest
awsTest