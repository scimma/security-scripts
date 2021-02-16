xcommands = [
["iam","get_account_authorization_details",['UserDetailList','GroupDetailList','RoleDetailList','Policies','IsTruncated',
                                            'Marker','ResponseMetadata']],
["iam","list_account_aliases",['AccountAliases','IsTruncated','ResponseMetadata']],
["route53","list_hosted_zones",['ResponseMetadata','HostedZones','IsTruncated','MaxItems']],
["ec2","describe_vpcs",['Vpcs','ResponseMetadata']],
["ec2","describe_subnets",['Subnets','ResponseMetadata']],
["ec2","describe_instances",['Reservations','ResponseMetadata']],
["ec2","describe_volumes",['Volumes','ResponseMetadata']],
["rds","describe_db_instances",['DBInstances','ResponseMetadata']],
["rds","describe_db_snapshots",['DBSnapshots','ResponseMetadata']],
["elb","describe_load_balancers",['LoadBalancerDescriptions','ResponseMetadata']],
["elbv2","describe_load_balancers",['LoadBalancers','ResponseMetadata']],
["redshift","describe_clusters",['Clusters','ResponseMetadata']],
["redshift","describe_cluster_subnet_groups",['ClusterSubnetGroups','ResponseMetadata']],
["sqs","list_queues",['ResponseMetadata']],
["sns","list_topics",['Topics','ResponseMetadata']],
["ec2","describe_security_groups",['SecurityGroups','ResponseMetadata']],
["ec2","describe_network_interfaces",['NetworkInterfaces','ResponseMetadata']],
["ec2","describe_vpc_peering_connections",['VpcPeeringConnections','ResponseMetadata']],
["autoscaling","describe_policies",['ScalingPolicies','ResponseMetadata']],
["autoscaling","describe_auto_scaling_groups",['AutoScalingGroups','ResponseMetadata']],
["cloudformation","describe_stacks",['Stacks','ResponseMetadata']],
["cloudfront","list_distributions",['ResponseMetadata','DistributionList']],
["cloudwatch","describe_alarms",['CompositeAlarms','MetricAlarms','ResponseMetadata']],
["config","describe_config_rules",['ConfigRules','ResponseMetadata']],
["ec2","describe_network_acls",['NetworkAcls','ResponseMetadata']],
["ec2","describe_route_tables",['RouteTables','ResponseMetadata']],
["ec2","describe_flow_logs",['FlowLogs','ResponseMetadata']],
["ec2","describe_vpc_endpoint_connections",['VpcEndpointConnections','ResponseMetadata']],
["ec2","describe_vpc_endpoints",['VpcEndpoints','ResponseMetadata']],
["ecr","describe_repositories",['repositories','ResponseMetadata']],
["elasticache","describe_cache_clusters",['CacheClusters','ResponseMetadata']],
["efs","describe_file_systems",['ResponseMetadata','FileSystems']],
["events","list_rules",['Rules','ResponseMetadata']],
["kms","list_keys",['Keys','Truncated','ResponseMetadata']],
["lambda","list_functions",['ResponseMetadata','Functions']],
["ecs","list_clusters",['clusterArns','ResponseMetadata']],
["logs","describe_destinations",['destinations','ResponseMetadata']],
["logs","describe_log_groups",['logGroups','ResponseMetadata']],
["logs","describe_resource_policies",['resourcePolicies','ResponseMetadata']],
["apigateway","get_rest_apis",['ResponseMetadata','items']],
["accessanalyzer","list_analyzers",['ResponseMetadata','analyzers']]
]

xcommands = [
    # nothing: ["iam", "get_account_password_policy",{}],
    # bucket policy got
    # nothing: ["ecr", "get_repository_policy",{"repositoryName":"ecr_describe_repositories.json|.[] | .repositories[] | .repositoryName"}],
    # nothing in glacier
    # kms empty



]

#policy_
xcommands = [
    # ["iam", "get_policy",{"PolicyArn":"iam_list_attached_user_policies.json|[.[] | .AttachedPolicies[] | .PolicyArn] | unique | .[]"}],
    # ["iam", "get_policy",{"PolicyArn":"iam_list_attached_role_policies.json|[.[] | .AttachedPolicies[] | .PolicyArn] | unique | .[]"}],
    # ["iam", "get_policy",{"PolicyArn":"iam_list_attached_group_policies.json|[.[] | .AttachedPolicies[] | .PolicyArn] | unique | .[]"}],
    # ["iam","list_entities_for_policy",{"PolicyArn":"iam_get_policy.json|.[] | .Policy.Arn"}],
# ["sns","list_topics",{}],
# ["sns","list_tags_for_resource",{"ResourceArn":"sns_list_topics.json|.[] |.Topics[]?|.TopicArn"}],

]

commands = [
# ["iam","get_account_authorization_details",{}],
# ["iam","list_account_aliases",{}],

# sns additions
["sns","list_topics",{}],
["sns","get_topic_attributes",{"TopicArn":"sns_list_topics.json|.[] |.Topics[]?|.TopicArn"}],
["sns", "list_subscriptions",{}],
["sns", "get_subscription_attributes",{"SubscriptionArn":"sns_list_subscriptions.json|.[] | .Subscriptions[] | .SubscriptionArn"}], # ok!
# ["sns", "list_platform_applications",{}], # useless, returns nothing


["secretsmanager","list_secrets",{}],
["secretsmanager","get_resource_policy",{"SecretId":"secretsmanager_list_secrets.json|.[]|.SecretList[]|.ARN"}], # not very useful... https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.get_resource_policy
# goes off name...

["s3","list_buckets",{}],
["s3","get_bucket_acl",{"Bucket":"s3_list_buckets.json|.[] | .Buckets[]?|.Name"}],  # bucket id not in response :(
["s3", "get_bucket_policy", {"Bucket":"s3_list_buckets.json|.[]|.Buckets[]?|.Name"}],  # no bucket id
["s3", "get_bucket_logging", {"Bucket":"s3_list_buckets.json|.[]|.Buckets[]?|.Name"}],  # empty
["s3", "get_bucket_location", {"Bucket": "s3_list_buckets.json|.[]|.Buckets[]?|.Name"}],  # no bucket id
["s3", "get_bucket_encryption", {"Bucket": "s3_list_buckets.json|.[]|.Buckets[]?|.Name"}],  # empty
["s3","get_bucket_tagging",{"Bucket":"s3_list_buckets.json|.[] | .Buckets[] | .Name"}],

# new cool stuff!
["ecr", "describe_repositories",{}],
["lambda", "get_policy", {"FunctionName":"lambda_list_functions.json|.[] | .Functions[]? | .FunctionName"}],

# cool policy stuff!
["iam", "list_groups",{}],
["iam", "list_attached_group_policies",{"GroupName":"iam_list_groups.json|.[] | .Groups[] | .GroupName"}],
["iam", "list_users",{}],
["iam", "list_attached_user_policies",{"UserName":"iam_list_users.json|.[] | .Users[] | .UserName"}],
["iam", "list_roles",{}],
["iam", "list_attached_role_policies",{"RoleName":"iam_list_roles.json|.[] | .Roles[] | .RoleName"}],

["resourcegroupstaggingapi","get_resources",{}],
["route53","list_hosted_zones",{}],
["ec2","describe_vpcs",{}],
["ec2","describe_subnets",{}],
["ec2","describe_instances",{}],
["ec2","describe_volumes",{}],
["rds","describe_db_instances",{}],
["rds","describe_db_snapshots",{}],
["elb","describe_load_balancers",{}],
["elbv2","describe_load_balancers",{}],
["redshift","describe_clusters",{}],
["redshift","describe_cluster_subnet_groups",{}],
["sqs","list_queues",{}],
["ec2","describe_security_groups",{}],
["ec2","describe_network_interfaces",{}],
["ec2","describe_vpc_peering_connections",{}],
["autoscaling","describe_policies",{}],
["autoscaling","describe_auto_scaling_groups",{}],
["cloudformation","describe_stacks",{}],
["cloudfront","list_distributions",{}],
# ["cloudwatch","describe_alarms",['CompositeAlarms','MetricAlarms','ResponseMetadata']],
# ["config","describe_config_rules",['ConfigRules','ResponseMetadata']],
["ec2","describe_network_acls",{}],
["ec2","describe_route_tables",{}],
["ec2","describe_flow_logs",{}],
["ec2","describe_vpc_endpoint_connections",{}],
["ec2","describe_vpc_endpoints",{}],
["ecr","describe_repositories",{}],
["elasticache","describe_cache_clusters",{}],
["efs","describe_file_systems",{}],
# ["events","list_rules",['Rules','ResponseMetadata']],
# ["kms","list_keys",['Keys','Truncated','ResponseMetadata']],
["lambda","list_functions",{}],
["ecs","list_clusters",{}],
# ["logs","describe_destinations",['destinations','ResponseMetadata']],
# ["logs","describe_log_groups",['logGroups','ResponseMetadata']],
# ["logs","describe_resource_policies",['resourcePolicies','ResponseMetadata']],
# ["apigateway","get_rest_apis",['ResponseMetadata','items']],
# ["accessanalyzer","list_analyzers",['ResponseMetadata','analyzers']]
]
