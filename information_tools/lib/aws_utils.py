"""
AWS Specifc utilities for general use.
"""

def shortened_arn(arn):
    """ make a short arn retaining summary info

    Short enough not oveflow tty lines.
    Long enough to give a clue.
    ARNS do _Not_ have a fixed format, AFAICT.
    """

    #ensure we are trying to deal with an ARN.
    components = arn.split(":")
    if components[0] != "arn" :
        return arn #can onyy abbreviate ARNs'
    if len(components) < 5  :
        return arn     #below will fail.
    aws_object = components[2] #resources manager
    aws_region = components[3] #region
    aws_thing = components[5].split('/')[0]  #specific resource
    short_arn = ':'.join([aws_object, components[3], aws_thing])
    return short_arn 


def decribe_regions_df(args):
    """ return a data frame enumerating all aws regions
        we can start an EC2 instance on
    
        Data frame has columns  'Endpoint' and 'Region'
    """
    import pandas as pd
    client = args.session.client('ec2')
    list = client.describe_regions()['Regions']
    df = pd.DataFrame.from_records(list)
    return df


    
