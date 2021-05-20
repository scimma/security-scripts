"""
A unit test for jget.JGet

Trace a samp,e CI to make sure get what we expect.

n.b. I think a unit test is good for all code we
intend to use in multiple lambdas,

"""

import unittest
import jget
import pprint

test_json = {
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
        "tags": [],
        "propagatingVgws": []
    },
    "supplementaryConfiguration": {}
}


class TestStringMethods(unittest.TestCase):

    def test_top_level(self):
        result = jget.Jget(test_json).at("configuration").get()
        #expect top level  json to be a dictionary
        self.assertTrue (type(result) == type ({}))
        self.assertTrue ('routes' in result)


    def test_traverse_array(self):
        result = jget.Jget(test_json).at("configuration").at("routes").get()
        #expect a list lenght two.
        self.assertTrue (type(result) == type ([]))
        self.assertTrue (len(result) == 2)
        self.assertTrue ('gatewayId' in result[0])
        self.assertTrue ('gatewayId' in result[1])
        

    def test_get_gateways(self):
        result = jget.Jget(test_json).at("configuration").at("routes").select("gatewayId").get()
        self.assertTrue (len(result) == 2)
        self.assertTrue (type(result) == type ([]))
        self.assertTrue ('local' in result)
        self.assertTrue ('igw-a5f227c1' in result)

if __name__ == '__main__':
    unittest.main()
    
