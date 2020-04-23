jqTest() {
    if hash jq 2>/dev/null; then
        echo "jq installed:  [  OK  ]"
    else
        echo "jq installed:  [FAILED]"
        echo "please install jq"
    fi
}

awsTest() {
    if hash aws 2>/dev/null; then
        echo "aws installed: [  OK  ]"
    else
        echo "aws installed: [FAILED]"
        echo "please install aws"
    fi
}

jqTest
awsTest