"""
Scenario: Subnet does not POssess a route table
        Return NOT_APPLICABLE

Scenario  Subnet does not have a route table  containing an internet Gateway
        Return NO_APPLICABLE

Scentaaion  Subnet has a route table that has an internet Gateay, bu subnet  flows ae not logged
        Return NON_COMPLIANT

Scenarion Subnet has a route table that has an internet Gateway, and subnet flows are logged.
        Retun COMPLIANT

"""

from rdklib import Evaluator, Evaluation, ConfigRule, ComplianceType

APPLICABLE_RESOURCES = ['AWS::EC2::Subnet']

class scimma_public_subnet_must_have_flows(ConfigRule):
    def evaluate_change(self, event, client_factory, configuration_item, valid_rule_parameters):
        ###############################
        # Add your custom logic here. #
        ###############################

        subnet =  configuration_item["subnetId"]
        print (subnet)
        # teh follwing can be used to find subnets with routes to the open internet
        #aws ec2 describe-route-tables | jq .[][].Associations[].SubnetId
        #aws ec2 describe-route-tables | jq .[][].Routes[].GatewayId
        #aws ec2 describe-route-tables | jq .[][].RouteTableId

        # how to find out if flows enabled?
        #aws ec2  describe-flow-logs  | jq .[][].ResourceId
        return [Evaluation(ComplianceType.NOT_APPLICABLE)]

    def evaluate_periodic(self, event, client_factory, valid_rule_parameters):
        pass

    def evaluate_parameters(self, rule_parameters):
        valid_rule_parameters = rule_parameters
        return valid_rule_parameters


################################
# DO NOT MODIFY ANYTHING BELOW #
################################
def lambda_handler(event, context):
    my_rule = scimma_public_subnet_must_have_flows()
    evaluator = Evaluator(my_rule, APPLICABLE_RESOURCES)
    return evaluator.handle(event, context)
