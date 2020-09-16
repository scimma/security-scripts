"""
AWS Specifc utilities for general use.
"""
import string


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
    aws_last_few_hex = arn[-3:]
    short_arn = ':'.join([aws_object, components[3], aws_thing, aws_last_few_hex])
    return short_arn 

def mostly_text(str):
    #A string is usef if > 5 non hex chars
    nchar = len(str)
    nhex = 0
    for char in str:
        if char in string.hexdigits : nhex += 1
    nonhex = nchar - nhex
    return (nonhex > 5)

def shortened_arn(arn):
    """ make a short arn retaining summary info

    Short enough not oveflow tty lines.
    Long enough to give a clue.
    ARNS do _Not_ have a fixed format, AFAICT.
    """

    #ensure we are trying to deal with an ARN.
    shortened_arn = []
    for component in  arn.split(":"):
        sublist = []
        for subcomponent in component.split("/"):
            if not mostly_text(subcomponent): continue
            sublist.append(subcomponent)
        component = "/".join(sublist)
        if not mostly_text(component): continue
        shortened_arn.append(component)
    last_few_hex = arn[-3:] #helps distinguish intances of the same
    shortened_arn.append(last_few_hex)
    shortened_arn = ':'.join(shortened_arn)
    return shortened_arn
    


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


    
