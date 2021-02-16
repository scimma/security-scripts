"""
Id map builder

This module makes intelligent guesses on where
Ids indicating various objects can be found in response files
"""
from security_scripts.information.lib import measurements
import os
import pyjq
import json


class Acquire(measurements.Dataset):
    """
    Clean aquired data, elevating it from L0A to L0B

    """

    def __init__(self, args, name, q):
        measurements.Dataset.__init__(self, args, name, q)
        self.table_name = "secrets"
        # dir enforcement
        self.l0b_dir = args.report_path + '/L0B/'
        self.l1_dir = args.report_path + '/L1/'
        if not os.path.exists(self.l1_dir):
            os.makedirs(self.l1_dir)

        self.make_data()
        self.clean_data()

    def has_suffix(self, s, suffix):
        """
        return True if staing has the indicated suffix
        """
        if s[-len(suffix):] == suffix:
            return True
        else:
            return False

    def trim_suffix(self, s, suffix):
        """
        return string with any suffix removed.
        """
        if s.endswith(suffix):
            s = s[:-len(suffix)]
        return s

    def trim_prefix(self, s, prefix):
        """
        return string with ssting up to matching initial prefix deleted
        """
        beg, pre, last = s.partition(prefix)
        if last: return last
        return s

    def trim_plural(self, s):
        """
        return string with any terminal s deleted
        """
        if s[-1] == 's':
            return s[:-1]
        else:
            return s

    def guess_L1_possible_links(self, records, my_service, my_function):
        """
        Identify links in the jq paths derived from a json file.

        For each identified link provide
        - the boto service
        - the boto function.
        - the link
        - a guess at the peer service the link is to

        return as a list of dictionaries.
        """

        # adding to a set will strikeout duplicates
        outset = set()
        for path in pyjq.all('paths(..)', records):
            last = path[-1]
            if type(last) == type("") and (self.has_suffix(last.lower(), "id")
                                           or self.has_suffix(last.lower(), "arn")
                                           or (self.has_suffix(last.lower(), "name") and 's3' in my_service.lower()) # s3 handling
                                           or (last.lower() == "bucket" and 's3' in my_service.lower())): # s3 handling
                # that got AutoScalingGroupARN
                peer_service = last
                if peer_service.lower() == 'arn' or peer_service.lower() == 'id':
                    # this happens if self id is merely an arn
                    # let's fix that
                    # happens to secretsmanager so far
                    peer_service = self.trim_suffix(my_function, 'manager')
                    peer_service = self.trim_prefix(peer_service, "get")
                    peer_service = self.trim_prefix(peer_service, "list")
                    peer_service = peer_service.replace("_", "")
                    peer_service = self.trim_plural(peer_service)
                peer_service = self.trim_suffix(peer_service, "Id")
                peer_service = self.trim_suffix(peer_service, "Arn")
                peer_service = peer_service.lower()
                # convert path to jq query pattern
                # this means....
                # a query fragment like
                #   dog.3.cat
                # goes to  dog.[].cat
                path = [".{}".format(e) if type(e) == type("") else "[]" for e in path]
                if path[0] == "[]": path[0] = ".[]"  # exception to resularity
                path = "".join(path)

                # hall of shame and cheating
                # shame upon amazon for having no naming convention whatsoever
                # cheating is me cheating to get it to work
                if my_service == 's3' and my_function == 'list_buckets':
                    peer_service = 'bucket'

                # take the tuples (which are hashable, and load into a dictionary.
                # put into hashable type so the python "set" can remove duplicates
                item = (my_service, my_function, path, peer_service)
                outset.add(item)



        dlist = []
        for item in outset:
            d = {}
            d["my_service"] = item[0]
            d["my_function"] = item[1]
            d["path"] = item[2]
            d["peer_service"] = item[3]
            dlist.append(d)
        return dlist

    def guess_if_is_self(self, d):
        """
        Annote a record with a  guess whether teh jqpath contained
        is a path to my own identifier bu setting "is_self" to be
        True or False.

        eg decide that a path ending in InstanceID is the path
        to self-identity in a record retured bu the ec2 service
        """
        my_id = None
        reference = None
        # here we ant to parse out the terminal name
        # from the jquery path. e.g. from ...
        # .[].LoadBalancerDescriptions[].Instances[].InstanceId
        # we want "instance"
        service_from_path = d["path"].split(".")[-1]
        service_from_path = service_from_path.lower()
        service_from_path = self.trim_suffix(service_from_path, "id")
        service_from_path = self.trim_suffix(service_from_path, "arn")
        # function here refers to the function in boto.
        # eg from describe_load_balancers we want...
        #  loadbalancer (no underscore, no plural
        my_function = d["my_function"]
        my_function = self.trim_prefix(my_function, "describe_")
        my_function = self.trim_prefix(my_function, "list_")
        my_function = self.trim_plural(my_function)
        my_function = my_function.replace("_", "")


        if my_function in service_from_path or (d['peer_service'].lower() in d['path'].lower() and
                                                d['peer_service'].lower() in d['my_function'].lower()):
            d["is_self"] = True
        else:
            d["is_self"] = False
        pass

    def make_data(self):
        """
        Main program
        -- Loop over all the L0B files
        -- Generate Lq draft taversal product.
        """
        master_list = []
        for record, basefilename in self.jsons_from_dir(self.l0b_dir):
            #process information to L0_B level
            # Extract meta data from (ugh) file name
            # string before the first _ is service
            # stings after the first _ are methods
            metadata  = basefilename.replace(".json","")
            service  = metadata.split("_")[0]
            function = "_".join(metadata.split("_")[1:])
            context = {"service" : service, "function" : function}
            dictlist = self.guess_L1_possible_links(record, service, function)
            master_list = master_list + dictlist

            # outset now containesx guesses at records that are either
            # identities of references.
            # now its time t seperate the tow at a guess level.
            for d in dictlist:
                self.guess_if_is_self(d)

        links_to_self   = [x for x in master_list if     x["is_self"]]
        links_to_others = [x for x in master_list if not x["is_self"]]

        json.dump(links_to_self,   open(self.l1_dir + "to_self.json"  ,"w"))
        json.dump(links_to_others, open(self.l1_dir + "to_others.json","w"))



