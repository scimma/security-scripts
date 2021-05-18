"""
Tiny library to traveres json, looking more like
declarations than proceduarl code

example:

gateways = Qson(test2).at("configuration").at("routes").select("gatewayId").get())

 
"""

test = {
          "dogs" : [
                     {"spaniel"  : {"name" : "dog1"}},
                     {"spaniel" : {"name" : "dog2"}},
                     {"bulldog" : {"color" : "dog3"}},
                    ],
          "cats" : {
                     "tiger" : {"habitat" : "Jungle"},
                     "lion"  : {"habitat" : "Savannah"}
                   }
        }

test2 = {
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


class Jget:
    """
    Very small and lightweight class for  extracting things from json.

    
    """
    def __init__ (self,json):

        # This variable is updated as the json is traversed
        # by successive function calls.
        # Once an array is traversed, it becomes an array of JSON
        
        self.json = json  

    def get(self):
        """
          return value(s) of query
          + Traversing to a terminal element returns a scalar,
            or list of scalars (if an array was invovled).
          * Travesals to nont termainal elements return json or
            a list of jsons if an array was traversed.
        """ 
        return self.json
    
    def at(self, string):
        """ Traverse a single named element"""
        self.json = self.json[string]
        return self
    
    def select(self,string):
        """ traverse an array, choosing array elements
            and then travere array elements beginning with string.
        """
        #choose array elements posessng staring.
        #return arra of what string pointss to
        self.json =[j[string] for j in self.json if string in j]
        return self
    

import pprint
pprint.pprint (Jget(test).get())
pprint.pprint (Jget(test).at("dogs").get()) 
pprint.pprint (Jget(test).at("dogs").select("spaniel").get())
pprint.pprint (Jget(test).at("dogs").select("spaniel").select("name").get())
pprint.pprint (Jget(test2).at("configuration").get())
pprint.pprint(Jget(test2).at("configuration").at("routes").get())
pprint.pprint (Jget(test2).at("configuration").at("routes").select("gatewayId").get())
        


