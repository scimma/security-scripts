from rdklib import Evaluator, Evaluation, ConfigRule, ComplianceType

APPLICABLE_RESOURCES = ['AWS::EC2::Subnet']

class scimma-public-subnet-must-have-flows(ConfigRule):
    def evaluate_change(self, event, client_factory, configuration_item, valid_rule_parameters):
        ###############################
        # Add your custom logic here. #
        ###############################


# teh follwing can be used to find subnets with routes to the open internet
#aws ec2 describe-route-tables | jq .[][].Associations[].SubnetId
#aws ec2 describe-route-tables | jq .[][].Routes[].GatewayId
#aws ec2 describe-route-tables | jq .[][].RouteTableId

# how to find out if flows enabled?
#aws ec2  describe-flow-logs  | jq .[][].ResourceId
        return [Evaluation(ComplianceType.NOT_APPLICABLE)]

    #def evaluate_periodic(self, event, client_factory, valid_rule_parameters):
    #    pass

    def evaluate_parameters(self, rule_parameters):
        valid_rule_parameters = rule_parameters
        return valid_rule_parameters


################################
# DO NOT MODIFY ANYTHING BELOW #
################################
def lambda_handler(event, context):
    my_rule = scimma-public-subnet-must-have-flows()
    evaluator = Evaluator(my_rule, APPLICABLE_RESOURCES)
    return evaluator.handle(event, context)
