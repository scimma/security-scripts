import sys
import unittest
from unittest.mock import MagicMock
import json
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
        raise Exception("Attempting to create an unknown client:", client_name)


sys.modules['boto3'] = Boto3Mock()

RULE = __import__('scimma-resources-have-required-tags')


class ComplianceTest(unittest.TestCase):

    rule_parameters = '{"SomeParameterKey":"SomeParameterValue","SomeParameterKey2":"SomeParameterValue2"}'

    invoking_event_template = {"configurationItem": {
         "relatedEvents": [],
         "relationships": [],
         "configuration": {},
         "tags": {},
         "configurationItemCaptureTime": "2018-07-02T03:37:52.418Z",
         "awsAccountId": "123456789012",
         "configurationItemStatus": "ResourceDiscovered",
         "resourceType": "AWS::IAM::Role",
         "resourceId": "some-resource-id",
         "resourceName": "some-resource-name",
         "ARN": "some-arn"},
         "notificationCreationTime": "2018-07-02T23:05:34.445Z",
         "messageType": "ConfigurationItemChangeNotification"
    }

    def setUp(self):
        pass

    def do_one_ci(self, ci, expected_response):
        """Check response given a file with a test CI"""

        # Build and configuration change event struxcture using the CI data ci file.
        #
        #  The layers of wrapping in the overall system is
        #  (config change (
        #   'invoking event (           all the following encoded...
        #      configurationItem (      ...in a json...
        #            configuration      ...string.
        #  )
        # ')))
        ci_resource = ci["resourceType"]
        ci_resourceId = ci["resourceId"]
        invoking_event = self.invoking_event_template
        invoking_event["configurationItem"] = ci
        invoking_event = json.dumps(invoking_event)
        ci_change_event = build_lambda_configurationchange_event(invoking_event)

        RULE.ASSUME_ROLE_MODE = False
        response = RULE.lambda_handler(ci_change_event, {})
        resp_expected = []
        resp_expected.append(build_expected_response(expected_response, ci_resourceId, ci_resource))
        assert_successful_evaluation(self, response, resp_expected)

    def test_no_tags_at_all(self):
        ci = {
            "version": "1.2",
            "accountId": "264683526309",
            "configurationItemCaptureTime": "2016-10-28T00:41:33.513Z",
            "configurationItemStatus": "OK",
            "configurationStateId": "1477615293513",
            "configurationItemMD5Hash": "4a857647e7ffd1495a78a76bccee9fd1",
            "arn": "arn:aws:ec2:us-east-1:264683526309:subnet/subnet-29428871",
            "resourceType": "AWS::EC2::Subnet",
            "resourceId": "subnet-29428871",
            "awsRegion": "us-east-1",
            "availabilityZone": "us-east-1a",
            "tags": {},
            "relatedEvents": [],
            "relationships": [
                {
                    "resourceType": "AWS::EC2::NetworkAcl",
                    "resourceId": "acl-b48fd1d0",
                    "relationshipName": "Is attached to NetworkAcl"
                },
                {
                    "resourceType": "AWS::EC2::NetworkInterface",
                    "resourceId": "eni-70a4b7bf",
                    "relationshipName": "Contains NetworkInterface"
                },
                {
                    "resourceType": "AWS::EC2::NetworkInterface",
                    "resourceId": "eni-c09a049e",
                    "relationshipName": "Contains NetworkInterface"
                },
                {
                    "resourceType": "AWS::EC2::Instance",
                    "resourceId": "i-ebf3e058",
                    "relationshipName": "Contains Instance"
                },
                {
                    "resourceType": "AWS::EC2::VPC",
                    "resourceId": "vpc-0990dc6d",
                    "relationshipName": "Is contained in Vpc"
                }
            ],
            "configuration": {
                "subnetId": "subnet-29428871",
                "state": "available",
                "vpcId": "vpc-0990dc6d",
                "cidrBlock": "172.31.16.0/20",
                "availableIpAddressCount": 4089,
                "availabilityZone": "us-east-1a",
                "defaultForAz": True,
                "mapPublicIpOnLaunch": True,
                "tags": []
            },
            "supplementaryConfiguration": {}
        }

        self.do_one_ci(ci, "NON_COMPLIANT")

    def test_lacks_service_tag(self):
        ci = {
            "version": "1.2",
            "accountId": "264683526309",
            "configurationItemCaptureTime": "2016-10-28T00:41:33.513Z",
            "configurationItemStatus": "OK",
            "configurationStateId": "1477615293513",
            "configurationItemMD5Hash": "4a857647e7ffd1495a78a76bccee9fd1",
            "arn": "arn:aws:ec2:us-east-1:264683526309:subnet/subnet-29428871",
            "resourceType": "AWS::EC2::Subnet",
            "resourceId": "subnet-29428871",
            "awsRegion": "us-east-1",
            "availabilityZone": "us-east-1a",
            "tags": {},
            "relatedEvents": [],
            "relationships": [
                {
                    "resourceType": "AWS::EC2::NetworkAcl",
                    "resourceId": "acl-b48fd1d0",
                    "relationshipName": "Is attached to NetworkAcl"
                },
                {
                    "resourceType": "AWS::EC2::NetworkInterface",
                    "resourceId": "eni-70a4b7bf",
                    "relationshipName": "Contains NetworkInterface"
                },
                {
                    "resourceType": "AWS::EC2::NetworkInterface",
                    "resourceId": "eni-c09a049e",
                    "relationshipName": "Contains NetworkInterface"
                },
                {
                    "resourceType": "AWS::EC2::Instance",
                    "resourceId": "i-ebf3e058",
                    "relationshipName": "Contains Instance"
                },
                {
                    "resourceType": "AWS::EC2::VPC",
                    "resourceId": "vpc-0990dc6d",
                    "relationshipName": "Is contained in Vpc"
                }
            ],
            "configuration": {
                "subnetId": "subnet-29428871",
                "state": "available",
                "vpcId": "vpc-0990dc6d",
                "cidrBlock": "172.31.16.0/20",
                "availableIpAddressCount": 4089,
                "availabilityZone": "us-east-1a",
                "defaultForAz": True,
                "mapPublicIpOnLaunch": True,
                "tags": [{"key": "Criticality", "value": "Production"}],
            },
            "supplementaryConfiguration": {}
        }

        self.do_one_ci(ci, "NON_COMPLIANT")

    def test_lacks_criticality_tag(self):
        ci = {
            "version": "1.2",
            "accountId": "264683526309",
            "configurationItemCaptureTime": "2016-10-28T00:41:33.513Z",
            "configurationItemStatus": "OK",
            "configurationStateId": "1477615293513",
            "configurationItemMD5Hash": "4a857647e7ffd1495a78a76bccee9fd1",
            "arn": "arn:aws:ec2:us-east-1:264683526309:subnet/subnet-29428871",
            "resourceType": "AWS::EC2::Subnet",
            "resourceId": "subnet-29428871",
            "awsRegion": "us-east-1",
            "availabilityZone": "us-east-1a",
            "tags": {},
            "relatedEvents": [],
            "relationships": [
                {
                    "resourceType": "AWS::EC2::NetworkAcl",
                    "resourceId": "acl-b48fd1d0",
                    "relationshipName": "Is attached to NetworkAcl"
                },
                {
                    "resourceType": "AWS::EC2::NetworkInterface",
                    "resourceId": "eni-70a4b7bf",
                    "relationshipName": "Contains NetworkInterface"
                },
                {
                    "resourceType": "AWS::EC2::NetworkInterface",
                    "resourceId": "eni-c09a049e",
                    "relationshipName": "Contains NetworkInterface"
                },
                {
                    "resourceType": "AWS::EC2::Instance",
                    "resourceId": "i-ebf3e058",
                    "relationshipName": "Contains Instance"
                },
                {
                    "resourceType": "AWS::EC2::VPC",
                    "resourceId": "vpc-0990dc6d",
                    "relationshipName": "Is contained in Vpc"
                }
            ],
            "configuration": {
                "subnetId": "subnet-29428871",
                "state": "available",
                "vpcId": "vpc-0990dc6d",
                "cidrBlock": "172.31.16.0/20",
                "availableIpAddressCount": 4089,
                "availabilityZone": "us-east-1a",
                "defaultForAz": True,
                "mapPublicIpOnLaunch": True,
                "tags": [{"key": "Service", "value": "anything will pass"}],
            },
            "supplementaryConfiguration": {}
        }

        self.do_one_ci(ci, "NON_COMPLIANT")

    def test_compliant(self):
        ci = {
            "version": "1.2",
            "accountId": "264683526309",
            "configurationItemCaptureTime": "2016-09-24T17:47:03.866Z",
            "configurationItemStatus": "OK",
            "configurationStateId": "949",
            "configurationItemMD5Hash": "89475da7d6c00dcd9ee1681a997d88ab",
            "arn": "arn:aws:ec2:us-east-1:264683526309:route-table/rtb-50b9b034",
            "resourceType": "AWS::EC2::RouteTable",
            "resourceId": "rtb-50b9b034",
            "awsRegion": "us-east-1",
            "availabilityZone": "Not Applicable",
            "tags": {},
            "relatedEvents": [
                "7656056e-4df8-4db6-a2fc-cf83e5461f7f"
            ],
            "relationships": [
                {
                    "resourceType": "AWS::EC2::VPC",
                    "resourceId": "vpc-0990dc6d",
                    "relationshipName": "Is contained in Vpc"
                }
            ],
            "configuration": {
                "routeTableId": "rtb-50b9b034",
                "vpcId": "vpc-0990dc6d",
                "routes": [
                    {
                        "destinationCidrBlock": "172.31.0.0/16",
                        "gatewayId": "local",
                        "state": "active",
                        "origin": "CreateRouteTable"
                    },
                    {
                        "destinationCidrBlock": "0.0.0.0/0",
                        "gatewayId": "igw-a5f227c1",
                        "state": "active",
                        "origin": "CreateRoute"
                    }
                ],
                "associations": [
                    {
                        "routeTableAssociationId": "rtbassoc-82f661e5",
                        "routeTableId": "rtb-50b9b034",
                        "main": True
                    }
                ],
                "tags": [{"key": "Service", "value": "anything will pass"},
                         {"key": "Criticality", "value": "Production"}],
                "propagatingVgws": []
            },
            "supplementaryConfiguration": {}
        }

        self.do_one_ci(ci, "COMPLIANT")

    def x_test_sample_2(self):
        RULE.ASSUME_ROLE_MODE = False
        response = RULE.lambda_handler(build_lambda_configurationchange_event(self.invoking_event_iam_role_sample, self.rule_parameters), {})
        resp_expected = []
        resp_expected.append(build_expected_response('NOT_APPLICABLE', 'some-resource-id', 'AWS::IAM::Role'))
        assert_successful_evaluation(self, response, resp_expected)

####################
# Helper Functions #
####################


def build_lambda_configurationchange_event(invoking_event, rule_parameters=None):
    event_to_return = {
        'configRuleName': 'myrule',
        'executionRoleArn': 'roleArn',
        'eventLeftScope': False,
        'invokingEvent': invoking_event,
        'accountId': '123456789012',
        'configRuleArn': 'arn:aws:config:us-east-1:123456789012:config-rule/config-rule-8fngan',
        'resultToken': 'token'
    }
    if rule_parameters:
        event_to_return['ruleParameters'] = rule_parameters
    return event_to_return


def build_lambda_scheduled_event(rule_parameters=None):
    invoking_event = '{"messageType":"ScheduledNotification","notificationCreationTime":"2017-12-23T22:11:18.158Z"}'
    event_to_return = {
        'configRuleName': 'myrule',
        'executionRoleArn': 'roleArn',
        'eventLeftScope': False,
        'invokingEvent': invoking_event,
        'accountId': '123456789012',
        'configRuleArn': 'arn:aws:config:us-east-1:123456789012:config-rule/config-rule-8fngan',
        'resultToken': 'token'
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
            test_class.assertEquals(resp_expected['Annotation'], response['Annotation'])
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
