import sys
import unittest
from unittest.mock import MagicMock
from botocore.exceptions import ClientError  #dlp

import botocore

##############
# Parameters #
##############

# Define the default resource to report to Config Rules
DEFAULT_RESOURCE_TYPE = 'AWS::::Account'

#############
# Main Code #
#############

CONFIG_CLIENT_MOCK = MagicMock()
STS_CLIENT_MOCK = MagicMock()

class Boto3Mock():
    @staticmethod
    def client(client_name, *args, **kwargs):
        if client_name == 'config':
            return CONFIG_CLIENT_MOCK
        if client_name == 'sts':
            return STS_CLIENT_MOCK
        raise Exception("Attempting to create an unknown client")

sys.modules['boto3'] = Boto3Mock()

RULE = __import__('scimma-s3-bucket-tagged')

class ComplianceTest(unittest.TestCase):

    # pull in the parameters as defined in the parameter file.
    # read the file as json, but caution. the AWS runtime...
    # ... framework Provides "InputParameters" as a string...
    # ... The framework anticipates that the string is valid JSON.
    # ... Note that th funcion we are testing recived this item
    # ... as JSON. 
    # ... don't thank me, thank this framework.
    import pdb ; pdb.set_trace()
    import json
    params=json.load(open('parameters.json','r'))
    rule_parameters = params["Parameters"]["InputParameters"]
    assert(type(rule_parameters) == type(""))

    # mock the "invoking event" that AWS would generate for a
    # configuration change.  the %s will hold the specifc
    # S3 bucket mock configuration for a test use case. That will
    # be filled out in the specfic test case. 
    invoking_event_template = '''{
    "configurationItem": %s ,
         "notificationCreationTime":"2018-07-02T23:05:34.445Z",
         "messageType":"ConfigurationItemChangeNotification"
    }'''

    def setUp(self):
        pass

    def test_sample(self):
        self.assertTrue(True)


    def test_empty_tags(self):
        RULE.ASSUME_ROLE_MODE = False
        with open("S3-empty-tags-CI.json",'r') as f: 
            CI = f.read()
        invoking_event = self.invoking_event_template % CI
        response = RULE.lambda_handler(build_lambda_configurationchange_event(invoking_event, self.rule_parameters), {})
        resp_expected = []
        resp_expected.append(build_expected_response('NON_COMPLIANT', 'mborch-test-bucket-config-item', 'AWS::S3::Bucket'))
        assert_successful_evaluation(self, response, resp_expected)

    def test_valid_criticality(self):
        RULE.ASSUME_ROLE_MODE = False
        with  open("S3-production-tags-CI.json",'r') as f: 
            CI = f.read()
        invoking_event = self.invoking_event_template % CI
        response = RULE.lambda_handler(build_lambda_configurationchange_event(invoking_event, self.rule_parameters), {})
        resp_expected = []
        resp_expected.append(build_expected_response('COMPLIANT', 'mborch-test-bucket-config-item', 'AWS::S3::Bucket'))
        assert_successful_evaluation(self, response, resp_expected)

    #def test_notags_at_all(self):
    #    RULE.ASSUME_ROLE_MODE = False
    #    response = RULE.lambda_handler(build_lambda_configurationchange_event(self.invoking_event_iam_role_sample, self.rule_parameters), {})
    #    resp_expected = []
    #    resp_expected.append(build_expected_response('NOT_APPLICABLE', 'some-resource-id', 'AWS::IAM::Role'))
    #    assert_successful_evaluation(self, response, resp_expected)

####################
# Helper Functions #
####################

def build_lambda_configurationchange_event(invoking_event, rule_parameters=None):
    event_to_return = {
        'configRuleName':'scimma-s3-bucket-tagged',
        'executionRoleArn':'roleArn',
        'eventLeftScope': False,
        'invokingEvent': invoking_event,
        'accountId': '123456789012',
        'configRuleArn': 'arn:aws:config:us-east-1:123456789012:config-rule/config-rule-8fngan',
        'resultToken':'token'
    }
    if rule_parameters:
        event_to_return['ruleParameters'] = rule_parameters
    return event_to_return

def build_lambda_scheduled_event(rule_parameters=None):
    invoking_event = '{"messageType":"ScheduledNotification","notificationCreationTime":"2017-12-23T22:11:18.158Z"}'
    event_to_return = {
        'configRuleName':'scimma-s3-bucket-tagged',
        'executionRoleArn':'roleArn',
        'eventLeftScope': False,
        'invokingEvent': invoking_event,
        'accountId': '123456789012',
        'configRuleArn': 'arn:aws:config:us-east-1:123456789012:config-rule/config-rule-8fngan',
        'resultToken':'token'
    }
    if rule_parameters:
        event_to_return['ruleParameters'] = rule_parameters
    return event_to_return

def build_expected_response(compliance_type, compliance_resource_id, compliance_resource_type=DEFAULT_RESOURCE_TYPE, annotation=None):
    if not annotation:
        return {
            'ComplianceType': compliance_type,
            'ComplianceResourceId': compliance_resource_id,
            'ComplianceResourceType': compliance_resource_type
            }
    return {
        'ComplianceType': compliance_type,
        'ComplianceResourceId': compliance_resource_id,
        'ComplianceResourceType': compliance_resource_type,
        'Annotation': annotation
        }

def assert_successful_evaluation(test_class, response, resp_expected, evaluations_count=1):
    if isinstance(response, dict):
        test_class.assertEqual(resp_expected['ComplianceResourceType'], response['ComplianceResourceType'])
        test_class.assertEqual(resp_expected['ComplianceResourceId'], response['ComplianceResourceId'])
        test_class.assertEqual(resp_expected['ComplianceType'], response['ComplianceType'])
        test_class.assertTrue(response['OrderingTimestamp'])
        if 'Annotation' in resp_expected or 'Annotation' in response:
            test_class.assertEqual(resp_expected['Annotation'], response['Annotation'])
    elif isinstance(response, list):
        test_class.assertEqual(evaluations_count, len(response))
        for i, response_expected in enumerate(resp_expected):
            test_class.assertEqual(response_expected['ComplianceResourceType'], response[i]['ComplianceResourceType'])
            test_class.assertEqual(response_expected['ComplianceResourceId'], response[i]['ComplianceResourceId'])
            test_class.assertEqual(response_expected['ComplianceType'], response[i]['ComplianceType'])
            test_class.assertTrue(response[i]['OrderingTimestamp'])
            if 'Annotation' in response_expected or 'Annotation' in response[i]:
                test_class.assertEqual(response_expected['Annotation'], response[i]['Annotation'])

def assert_customer_error_response(test_class, response, customer_error_code=None, customer_error_message=None):
    if customer_error_code:
        test_class.assertEqual(customer_error_code, response['customerErrorCode'])
    if customer_error_message:
        test_class.assertEqual(customer_error_message, response['customerErrorMessage'])
    test_class.assertTrue(response['customerErrorCode'])
    test_class.assertTrue(response['customerErrorMessage'])
    if "internalErrorMessage" in response:
        test_class.assertTrue(response['internalErrorMessage'])
    if "internalErrorDetails" in response:
        test_class.assertTrue(response['internalErrorDetails'])

def sts_mock():
    assume_role_response = {
        "Credentials": {
            "AccessKeyId": "string",
            "SecretAccessKey": "string",
            "SessionToken": "string"}}
    STS_CLIENT_MOCK.reset_mock(return_value=True)
    STS_CLIENT_MOCK.assume_role = MagicMock(return_value=assume_role_response)

##################
# Common Testing #
##################

class TestStsErrors(unittest.TestCase):

    def xtest_sts_unknown_error(self):
        RULE.ASSUME_ROLE_MODE = True
        RULE.evaluate_parameters = MagicMock(return_value=True)
        STS_CLIENT_MOCK.assume_role = MagicMock(side_effect=ClientError(
            {'Error': {'Code': 'unknown-code', 'Message': 'unknown-message'}}, 'operation'))
#dlp    STS_CLIENT_MOCK.assume_role = MagicMock(side_effect=botocore.exceptions.ClientError(
#Dlp        {'Error': {'Code': 'unknown-code', 'Message': 'unknown-message'}}, 'operation'))
        response = RULE.lambda_handler(build_lambda_configurationchange_event('{}'), {})
        assert_customer_error_response(
            self, response, 'InternalError', 'InternalError')

    def xtest_sts_access_denied(self):
        RULE.ASSUME_ROLE_MODE = True
        RULE.evaluate_parameters = MagicMock(return_value=True)
#dlp        STS_CLIENT_MOCK.assume_role = MagicMock(side_effect=botocore.exceptions.ClientError(
#dlp        {'Error': {'Code': 'AccessDenied', 'Message': 'access-denied'}}, 'operation'))
        STS_CLIENT_MOCK.assume_role = MagicMock(ClientError(
           {'Error': {'Code': 'AccessDenied', 'Message': 'access-denied'}}, 'operation'))
        response = RULE.lambda_handler(build_lambda_configurationchange_event('{}'), {})
        assert_customer_error_response(
            self, response, 'AccessDenied', 'AWS Config does not have permission to assume the IAM role.')
