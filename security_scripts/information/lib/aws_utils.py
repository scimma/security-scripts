"""
AWS Specifc utilities for general use.
"""
import string


def Original_shortened_arn(arn):
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
    # aws_region = components[3] #region
    aws_thing = components[5].split('/')[0]  #specific resource
    aws_last_few_hex = arn[-3:]
    short_arn = ':'.join([aws_object, components[3], aws_thing, aws_last_few_hex])
    return short_arn 


def next_are_hex(strlist):
    if strlist[0] not in string.hexdigits: return False
    if strlist[1] not in string.hexdigits: return False
    if strlist[2] not in string.hexdigits: return False
    return True

def clean_hex(str):

    str = str+"000"  #pad
    clist = [c for c in str]
    outlist =[]
    stop_chars = ":/-"
    while len(clist) > 4:
        c = clist.pop(0)
        outlist.append(c)
        if c in stop_chars and  next_are_hex(clist):
            while len(clist) != 0 and clist[0] in string.hexdigits: clist.pop(0)
    return "".join(outlist)

def shortened_arn(arn):
    """ make a short arn retaining summary info

    Short enough not oveflow tty lines.
    Long enough to give a clue.
    ARNS do _Not_ have a fixed format, AFAICT.
    """

    #ensure we are trying to deal with an ARN.

    arn = arn.split(":")
    arn = ":".join(arn[2:])
    tail = arn[-3:]
    arn = clean_hex(arn)
    arn = arn + tail
    return arn
    

all_regions_cache = None

def decribe_regions_df(args):
    """ return a data frame enumerating all aws regions
        we can start an EC2 instance on
    
        Data frame has columns  'Endpoint' and 'Region'
    """
    global all_regions_cache
    if all_regions_cache is None:
        import pandas as pd
        client = args.session.client('ec2')
        list = client.describe_regions()['Regions']
        df = pd.DataFrame.from_records(list)
        all_regions_cache = df # call this instead
    return all_regions_cache


    
